'''
Compute cosine similarity between regions from TFIDF scores across beers
'''
import pandas as pd
import pymysql as mdb
import numpy as np
from authent import dbauth as authsql

def dbconnect():
    # connect to database
    con=mdb.connect(**authsql)
    return con

def readTFIDF(con):
    # impor data from database
    sql='''
    SELECT beerid,locbinid,TFIDF
    FROM tfidf
    '''
    df=pd.io.sql.read_frame(sql,con)
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

def getRegionExample(con):
    # look up in database the city with most tweets in region
    sql='''
    SELECT a.locbinid,a.cityid,a.beercount, us.fullname
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
    df=pd.io.sql.read_frame(sql,con)
    return df

def main():
    # run
    con=dbconnect()
    df=readTFIDF(con)
    S,N=makeSimMat(df)
    return S
    