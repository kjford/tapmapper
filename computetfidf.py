'''
Perform TF-IDF normalization on processed tweets
using regions as documents, and beers as terms
'''

import pandas as pd
import pymysql as mdb
import numpy as np
from authent import dbauth as authsql

# import data from database
con=mdb.connect(**authsql)
with con:
    # load processed tweets that have cityid
    sql='''
    SELECT beerid,locbinid
    FROM procbintweets
    '''
    df=pd.io.sql.read_frame(sql,con)

# get term frequencies, un-normalized to region size
# construct beerid,locbinid list
tfBid=[] #beers
tfLid=[] #locations
tfValue=[] # term frequency value
# get in number of regions
N = len(df['locbinid'].unique())
idfValue=[]

for bid,gr in df.groupby('beerid'):
    for lid,gr2 in gr.groupby('locbinid'):
        tfBid.append(int(bid))
        tfLid.append(int(lid))
        tfValue.append(1.0*len(gr2))
        idfValue.append(1.0*len(gr))
tfValue=np.array(tfValue)
idfValue=np.array(idfValue)
idfValue=np.log(1.0*N/(1.0+idfValue))

tfidf=tfValue*idfValue

# add back to database in tfidf table
# cast the numpy arrays back to lists of floats
tfValue = [float(x) for x in tfValue]
idfValue = [float(x) for x in idfValue]
tfidf = [float(x) for x in tfidf]

vals=zip(tfBid,tfLid,tfValue,idfValue,tfidf)

with con:
    cur=con.cursor()
    # make table
    cur.execute("""DROP TABLE IF EXISTS tfidf;""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tfidf(
        tfidfid INT AUTO_INCREMENT PRIMARY KEY,
        beerid INT,
        locbinid INT,
        TF DOUBLE,
        IDF DOUBLE,
        TFIDF DOUBLE
        )
        """)
    # add to table
    insql='''
    INSERT INTO tfidf
    (beerid,locbinid,TF,IDF,TFIDF)
    VALUES(
    %s,%s,%s,%s,%s)
    '''
    cur.executemany(insql,vals)
