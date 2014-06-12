'''
get initial beer tweet database from search api
'''
import pandas as pd
import numpy as np
import cPickle
#import MySQLdb as mdb
import pymysql as mdb
import time
import twittertools
from authent import dbauth as authsql

# load beer names with >500 ratings

sql='''
    SELECT beers.beername, beers.id
    FROM beers
    JOIN revstats ON beers.id=revstats.id
    WHERE revstats.nreviews>500;
    '''

con=mdb.connect(**authsql)
print 'Loading beer names'
df=pd.io.sql.read_frame(sql,con)
beers=list(df['beername'])
ids=list(df['id'])
totalnum=len(beers)
print 'Found %i beers'%totalnum

# search twitter for beers and save out to dataframe
count=0
tweetholder=[]
for bn in beers:
    searchstr='"'+bn+'"'
    print 'On %i of %i'%(count+1,totalnum)
    parsedres = twittertools.TwitSearch(searchstr,twittertools.twitAPI)
    tweetholder.append(parsedres)
    count+=1
print('Done.')
# save
timeint = np.int(time.time())
cPickle.dump(tweetholder,open('tweetsearch_%i.cpk'%timeint,'w'))