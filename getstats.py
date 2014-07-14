'''
Data exploration functions
'''


import pymysql as mdb
import pandas as pd
import numpy as np
from authent import dbauth as authsql

from datetime import datetime

con=mdb.connect(**authsql)


def dayofweek(condb=con):
    from matplotlib import pylab as plt
    # plot processed tweet volume binned by weekday in the past week
    sql='''
        select dayname(convert_tz(tweettime,'GMT','US/Pacific')) as dayofweek, count(distinct rawid) as cnt
        from procbintweets
        join processedtweets
        on procbintweets.proctweetid=processedtweets.proctwid
        where date(convert_tz(tweettime,'GMT','US/Pacific'))>=date_sub(convert_tz(current_date(),'GMT','US/Pacific'),INTERVAL 28 DAY)
        group by dayofweek
        '''
    df=pd.io.sql.read_sql(sql,condb)
    df.plot(x='dayofweek', y='cnt')
    return df

def hourly(condb=con, hrbin=6, ndays=14):
    from matplotlib import pylab as plt
    # plot 
    sql='''
        select convert_tz(tweettime,'GMT','US/Pacific') as time, 
        min(convert_tz(tweettime,'GMT','US/Pacific')) as hourbin, 
        dayname(convert_tz(tweettime,'GMT','US/Pacific')) as dow, 
        count(distinct rawid) as cnt
        from procbintweets
        join processedtweets
        on procbintweets.proctweetid=processedtweets.proctwid
        where date(convert_tz(tweettime,'GMT','US/Pacific'))>=date_sub(convert_tz(current_date(),'GMT','US/Pacific'),INTERVAL {0} DAY)
        group by concat(date(time),hour(time) div {1})
        '''.format(ndays,hrbin)
    df=pd.io.sql.read_sql(sql,condb)
    # clean the time names to day of week and hour like 'Mo 12' for monday 12to12+hrbin
    df['cleantime']=df.apply(lambda row: str(row['dow'])[:2] + str(row['hourbin'])[-9:-6],axis=1)
    df.plot(x='cleantime', y='cnt')
    return df

def beersnob(condb=con, minct=50):
    # get the beer snob score of cities: avg (tfidf * beerrating)
    # import data from database
    sql_tfidf='''
    SELECT t.beerid,t.locbinid,t.TFIDF, t.TF, r.avgoverall
    FROM tfidf as t
    join revstats as r
    on t.beerid=r.id
    '''
    TFIDFdf=pd.io.sql.read_sql(sql_tfidf,condb)
    #print TFIDFdf
    # look up in database the city with most tweets in region
    sql_city='''
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
    HAVING a.beercount>={0}
    ORDER BY a.beercount
    '''.format(minct)
    CNdf=pd.io.sql.read_sql(sql_city,condb)
    #print CNdf
    # group by region and compute snob score
    CNdf['snobscore']=np.zeros(len(CNdf))
    for rid,gr in TFIDFdf.groupby('locbinid'):
        # see if this region is in the dataframe of named regions with enough beer counts
        if rid in CNdf['locbinid']:
            # get the index
            currind = CNdf['locbinid'][CNdf['locbinid']==rid].index[0]
            snobscore=np.mean(np.array(gr['TFIDF']) * np.array(gr['avgoverall']))
            CNdf['snobscore'][currind]=snobscore
    return CNdf

if __name__=='__main__':
    # make some output files that might end up on the page
    destination='./app/static/'
    cndf=beersnob(condb=con, minct=50).sort('snobscore')
    cndf['fullname'].to_json(destination+'snob.json',orient='values')
    