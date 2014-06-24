import pymysql as mdb
import pandas as pd
import numpy as np
from authent import dbauth as authsql


con=mdb.connect(**authsql)


sql='''
select dayname(convert_tz(tweettime,'GMT','US/Pacific')) as dayofweek, count(distinct rawid) as cnt
from procbintweets
join processedtweets
on procbintweets.proctweetid=processedtweets.proctwid
where date(convert_tz(tweettime,'GMT','US/Pacific'))>=date_sub(current_date(),INTERVAL 8 DAY)
group by dayofweek
'''

df=pd.io.sql.read_sql(sql,con)
