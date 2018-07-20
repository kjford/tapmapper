"""
Compute cosine similarity between regions from TFIDF scores across beers
"""
from tapmapper.database import session_scope, engine
from tapmapper import models as m
import pandas as pd
import numpy as np


def read_tfidf():
    # import data from database
    # to do: this should really be stashed
    with session_scope() as s:
        q = s.query(m.Tfidf)
        data = [{'beerid': x.beerid,
                 'locbinid': x.locbinid,
                 'TFIDF': x.TFIDF} for x in q]

    df = pd.DataFrame(data)
    return df


def cosinesim(v1, v2):
    # cosine similarity between 2 vectors
    cs=v1.dot(v2.T) / (np.sqrt(v1.dot(v1.T)) * np.sqrt(v2.dot(v2.T)))
    return cs


def make_sim_mat(df):
    """
    make similarity matrix using cosine similarity between
    pairs of TFIDF scores
    first make N (regions) by B (unique beerids)
    set of features from TFIDF scores
    """
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
        rvec=featvec[r,:]/featvec[r,:].sum()
        for r2 in xrange(0,r):
            s=cosinesim(rvec,featvec[r2,:]/(featvec[r2,:].sum()))
            S[r,r2]=s
            S[r2,r]=s
            # waste of space to store twice, but this won't ever be that big
    # return along with unique indices of regions
    return S,N


def make_sim_vec(df, regid):
    # rather than make the entire similarity matrix, just get similarity vector for
    # region of interest
    B = df['beerid'].unique()
    N = df['locbinid'].unique()
    featvec = np.zeros((len(N),len(B)))
    # go through data frame and add TFIDF to feature vectors
    for _, rowdata in df.iterrows():
        beer = rowdata['beerid']
        region = rowdata['locbinid']
        score = rowdata['TFIDF']
        beerind = np.where(B == beer)[0][0]
        regind = np.where(N == region)[0][0]
        featvec[regind, beerind] = score
    
    S = np.zeros((len(N)))
    roi = np.where(N == regid)[0][0]
    # compute similarity scores
    roivec = featvec[roi, :]/featvec[roi, :].sum()
    for r in xrange(len(N)):
        S[r] = cosinesim(featvec[r, :] / featvec[r,:].sum(), roivec)
    return S, N


def get_region_example():
    # look up in database the city with most tweets in region
    # fix me
    sql="""
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
    """
    df=pd.read_sql(sql, engine)
    return df


def output_region_points():
    # output in json like formate the region id's, names, and lat+lon
    df = get_region_example()
    df = df.set_index('locbinid') #index by region
    inds = list(df.index)
    bc = df.beercount.tolist()
    fn = df.fullname.tolist()
    lats = df.lat.tolist()
    lngs = df.lng.tolist()
    output = []
    for i in xrange(len(df)):
        output.append({'regionid': inds[i],
                       'beercount': bc[i],
                       'fullname': fn[i],
                       'lat': lats[i],
                       'lng': lngs[i],
                       'similarity': bc[i]})
    return output


def get_simdata(regid):
    # get tf-idf similarity scores
    tfidf = read_tfidf()
    S, N = make_sim_vec(tfidf, regid)
    # get labels and coordinates for region ids
    rtitles = get_region_example()
    # turn into a dictionary
    a = rtitles.set_index('locbinid')  # index by region
    b = pd.DataFrame({'similarity': S}, index=N)
    combdf_raw=a.join(b)  # joined on index so now combdf.ix[regid] has all
    combdf = combdf_raw.sort_values('similarity', ascending=False)
    inds=list(combdf.index)
    bc = combdf.beercount.tolist()
    fn = combdf.fullname.tolist()
    lats = combdf.lat.tolist()
    lngs = combdf.lng.tolist()
    sim = combdf.similarity.tolist()
    output = []
    taketop = np.minimum(len(N),20)
    for i in xrange(taketop):
        output.append({'regionid': inds[i],
                       'beercount': bc[i],
                       'fullname': fn[i],
                       'lat': lats[i],
                       'lng': lngs[i],
                       'similarity': sim[i]})
    return output
