'''
Compute cosine similarity between regions from TFIDF scores across beers
'''
import pandas as pd
import numpy as np

def readTFIDF(con):
    # import data from database
    sql='''
    SELECT beerid,locbinid,TFIDF
    FROM tfidf
    '''
    df=pd.io.sql.read_sql(sql,con)
    return df

def cosinesim(v1,v2):
    # cosine similarity between 2 vectors
    cs=v1.dot(v2.T) / (np.sqrt(v1.dot(v1.T)) * np.sqrt(v2.dot(v2.T)))
    return cs
    
def makeSimMat(df):
    # make similarity matrix using cosine similarity between pairs of TFIDF scores
    # first make N (regions) by B (unique beerids) set of features from TFIDF scores
    B=df['beerid'].unique()
    N=df['locbinid'].unique()
    featvec=np.zeros((len(N),len(B)))
    # go through data frame and add TFIDF to feature vectors
    for _,rowdata in df.iterrows():
        beer=rowdata['beerid']
        region=rowdata['locbinid']
        score=rowdata['TFIDF']
        beerind=np.where(B==beer)[0][0]
        regind=np.where(N==region)[0][0]
        featvec[regind,beerind]=score
    
    S = np.zeros((len(N),len(N)))
    # compute similarity matrix
    for r in xrange(len(N)):
        for r2 in xrange(0,r):
            S[r,r2]=cosinesim(featvec[r,:],featvec[r2,:])
            S[r2,r]=cosinesim(featvec[r,:],featvec[r2,:])
            # waste of space to store twice, but this won't ever be that big
    # return along with unique indices of regions
    return S,N

def makeSimVec(df,regid):
    # rather than make the entire similarity matrix, just get similarity vector for
    # region of interest
    B=df['beerid'].unique()
    N=df['locbinid'].unique()
    featvec=np.zeros((len(N),len(B)))
    # go through data frame and add TFIDF to feature vectors
    for _,rowdata in df.iterrows():
        beer=rowdata['beerid']
        region=rowdata['locbinid']
        score=rowdata['TFIDF']
        beerind=np.where(B==beer)[0][0]
        regind=np.where(N==region)[0][0]
        featvec[regind,beerind]=score
    
    S = np.zeros((len(N)))
    roi=np.where(N==regid)[0][0]
    # compute similarity scores
    roivec=featvec[roi,:]/featvec[roi,:].sum()
    for r in xrange(len(N)):
        S[r]=cosinesim(featvec[r,:]/featvec[r,:].sum(),roivec)
    return S,N

def getRegionExample(con):
    # look up in database the city with most tweets in region
    sql='''
    SELECT a.locbinid,a.cityid,a.beercount, us.fullname, us.lat, us.lng
    FROM ( 
       SELECT p.locbinid,p.cityid,count(p.beerid) as beercount
       FROM procbintweets as p
       GROUP BY p.cityid
       ORDER BY beercount DESC
       ) as a
    JOIN uscities AS us
    ON a.cityid=us.cityid
    GROUP BY a.locbinid
    ORDER BY a.beercount
    '''
    df=pd.io.sql.read_sql(sql,con)
    return df

def getSimdata(con,regid):
    # get tf-idf similarity scores
    tfidf=readTFIDF(con)
    S,N=makeSimVec(tfidf,regid)
    # get labels and coordinates for region ids
    rtitles=getRegionExample(con)
    # turn into a dictionary
    a=rtitles.set_index('locbinid') #index by region
    b=pd.DataFrame({'similarity':S},index=N)
    combdf_raw=a.join(b) # joined on index so now combdf.ix[regid] has all
    combdf=combdf_raw.sort(columns='similarity',ascending=False)
    inds=list(combdf.index)
    bc=combdf.beercount.tolist()
    fn=combdf.fullname.tolist()
    lats=combdf.lat.tolist()
    lngs=combdf.lng.tolist()
    sim=combdf.similarity.tolist()
    output=[]
    taketop = np.minimum(len(N),20)
    for i in xrange(taketop):
        output.append({'regionid':inds[i],\
                       'beercount':bc[i],\
                       'fullname':fn[i],\
                       'lat':lats[i],\
                       'lng':lngs[i],
                       'similarity':sim[i]})
    
    
    return output
    