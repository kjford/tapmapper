'''
Validation of tfidf model for beers in cities

Assumption:
Locals will tweet more about beers that are brewed locally

Validation:
For beers with brewers in US (that I have lat/lng for):
For each region/city:
Get distance to brewer / TF-IDF (where TF-IDF > 1)
lower score is small distance with high tf-idf
compare actual for each region 
to randomized shuffle of beers with equal partitioning
'''

import pymysql as mdb
import pandas as pd
import numpy as np
from authent import dbauth as authsql

def condb():
    con=mdb.connect(**authsql)
    return con

def readTFIDF(con):
    # load tweets that are binned by region and associated with a beer
    # get region coordinates and brewer coordinates
    print 'Loading data...'
    sql='''
    SELECT p.beerid,p.locbinid,regloc.reglat as R_Lat,regloc.reglng as R_Lng,us.lat as BR_Lat,us.lng as BR_Lng
    FROM procbintweets as p
    JOIN beers as b
    ON p.beerid=b.id
    JOIN brewers as br
    ON b.brewerid=br.brewerid
    LEFT OUTER JOIN uscities as us
    ON br.location = us.fullname
    JOIN (
    SELECT a.locbinid,us2.lat as reglat, us2.lng as reglng
    FROM ( 
       SELECT p2.locbinid,p2.cityid,count(p2.beerid) as beercount
       FROM procbintweets as p2
       GROUP BY p2.cityid
       ORDER BY beercount DESC
       ) as a
    JOIN uscities AS us2
    ON a.cityid=us2.cityid
    GROUP BY a.locbinid
    ) as regloc
    ON regloc.locbinid=p.locbinid    
    '''
    df=pd.io.sql.read_sql(sql,con)
    print 'Done.'
    return df

def distcalc(lat1,lng1,lat2,lng2):
    # for western hemisphere need to flip the sign of lng
    # degree to rad
    lat1r= np.pi *lat1/180.0
    lat2r= np.pi *lat2/180.0
    lng1r= -np.pi *lng1/180.0
    lng2r= -np.pi *lng2/180.0
    # distance in units of sphere radius
    d=np.arccos(np.sin(lat1r) * np.sin(lat2r) + np.cos(lat1r) * np.cos(lat2r) * np.cos(lng2r-lng1r))
    return d*3863.191 # in miles


def regionalscore(df):
    # compute distance/tf-idf
    tfBid=[] #beers
    tfLid=[] #locations
    tfValue=[] # term frequency value
    # get in number of regions
    N = len(df['locbinid'].unique())
    idfValue=[]
    distValue = []
    
    for bid,gr in df.groupby('beerid'):
        nuniqueloc=len(gr['locbinid'].unique())
        blat=gr['BR_Lat'].unique()[0]
        blng=gr['BR_Lng'].unique()[0] #only one
        for lid,gr2 in gr.groupby('locbinid'):
            tfBid.append(int(bid))
            tfLid.append(int(lid))
            tfValue.append(1.0*len(gr2))
            idfValue.append(1.0*nuniqueloc)
            rlat=blat=gr2['R_Lat'].unique()[0]
            rlng=gr2['R_Lng'].unique()[0]
            # quick and dirty distance (planar)
            # distValue.append(np.sqrt((blat-rlat)**2 + (blng-rlng)**2))
            # actual distance in miles
            distValue.append(distcalc(blat,blng,rlat,rlng))
    tfValue=np.array(tfValue) # this is not normalized to number of tweets in region
    # normalize tf by number of tweets in the region
    tweetsperregion=[]
    tfLid=np.array(tfLid)
    for j in tfLid:
        tweetsperregion.append(np.sum(tfLid==j))
    tfValue=tfValue/tweetsperregion
    idfValue=np.array(idfValue)
    idfValue=1.0+np.log(1.0*N/(idfValue))

    tfidf=tfValue*idfValue
    regscore = [np.array(distValue),tfidf]
    return regscore



def beercountbycity(df):
    # compute distance/tf-idf
    tfBid=[] #beers
    tfLid=[] #locations
    tfValue=[] # term frequency value
    # get in number of regions
    N = len(df['locbinid'].unique())
    distValue = []
    
    for bid,gr in df.groupby('beerid'):
        nuniqueloc=len(gr['locbinid'].unique())
        blat=gr['BR_Lat'].unique()[0]
        blng=gr['BR_Lng'].unique()[0] #only one
        for lid,gr2 in gr.groupby('locbinid'):
            tfBid.append(int(bid))
            tfLid.append(int(lid))
            tfValue.append(1.0*len(gr2)) # number of beer mentions in city
            rlat=blat=gr2['R_Lat'].unique()[0]
            rlng=gr2['R_Lng'].unique()[0]
            distValue.append(distcalc(blat,blng,rlat,rlng))
    tfValue=np.array(tfValue) # this is not normalized to number of tweets in region
    
    regscore = [np.array(distValue),tfValue]
    return regscore




def randomizeDF(df):
    # permute the data frame to randomize beer-region interactions
    # break apart into beer and regions
    nrows=len(df)
    rperm=np.random.permutation(nrows)
    beerids=np.array(df.beerid)
    beerlat=np.array(df.BR_Lat)
    beerlng=np.array(df.BR_Lng)
    randdf = df[['locbinid','R_Lat','R_Lng']]
    randdf['beerid']=beerids[rperm]
    randdf['BR_Lat']=beerlat[rperm]
    randdf['BR_Lng']=beerlng[rperm]
    return randdf

def TFIDFvsbinDist(tfidf,distarr,binsize=50,maxbin=2000):
    # bin tfidf-distarr pairs into distance bins and take average tfidf in bin
    # or counts (which =  presence of tweet in region)
    xbins=np.arange(0,maxbin,binsize)
    # only care about ones that have real positive distances
    distarr=distarr[distarr>=0]
    tfidf=tfidf[distarr>=0]
    # digitize the distances
    dbins=np.digitize(distarr,xbins)
    counts=np.zeros(len(xbins))
    for i in xrange(len(xbins)):
        # average tfidf
        #counts[i]=(tfidf[dbins==(i+1)]).mean()
        # or counts of tweets:
        counts[i]=len(tfidf[dbins==(i+1)])
    return [counts,xbins]

def BeerCntvsbinDist(cntarr,distarr,binsize=50,maxbin=2000):
    # bin cntarr-distarr pairs into distance bins and take sum in bin
    xbins=np.arange(0,maxbin,binsize)
    # only care about ones that have real positive distances
    distarr=distarr[distarr>=0]
    cntarr=cntarr[distarr>=0]
    # digitize the distances
    dbins=np.digitize(distarr,xbins)
    counts=np.zeros(len(xbins))
    for i in xrange(len(xbins)):
        #counts of tweets:
        counts[i]=np.sum(cntarr[dbins==(i+1)])
    return [counts,xbins]



if __name__=='__main__':
    # run permutation analysis
    n=100
    con=condb()
    df=readTFIDF(con)
    blscore = beercountbycity(df)
    perscores=[]
    print 'Running permutation analysis'
    for i in xrange(n):
        print 'permutation %i'%i
        newdf=randomizeDF(df)
        perscores.append(beercountbycity(newdf))
    blarray=np.array(blscore)
    permarray=np.array(perscores)
    # bin by distance
    binneddata=BeerCntvsbinDist(blarray[1],blarray[0])
    dataavg=binneddata[0]
    xbins=binneddata[1]
    count=0
    permtfidfvd=np.zeros((n,len(binneddata[1])))
    for p in permarray:
        permtfidfvd[count,:]=np.array(BeerCntvsbinDist(p[1],p[0]))[0]
        count+=1
    permavg=permtfidfvd.mean(axis=0)
    
    
    
    