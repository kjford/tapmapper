import pymysql as mdb
import pandas as pd
import numpy as np
from authent import dbauth as authsql


con=mdb.connect(**authsql)


sql='''
select tweettime, count(distinct rawid) as cnt
from procbintweets
join processedtweets
on procbintweets.proctweetid=processedtweets.proctwid
group by day(tweettime)
'''

df=pd.io.sql.read_sql(sql,con)
