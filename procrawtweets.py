'''
process raw tweets:
search each raw tweet across beer names and beer name variants
associate tweets with beer name id if found
add to processedtweets table (create if doesn't exist)
'''

import pandas as pd
import pymysql as mdb
import numpy as np
from authent import dbauth as authsql

# clunky hack that needs work:
# start processing mysql data base from id >= minid
with open('rawtweetprocid.txt','r') as f:
    minid=int(f.read())

con=mdb.connect(**authsql)
with con:
    # create table for processed tweets
    cur=con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS processedtweets(
        proctwid INT AUTO_INCREMENT PRIMARY KEY,
        rawid BIGINT,
        tweetid BIGINT, 
        tweetloc VARCHAR(150),
        tweettext TEXT,
        tweettime DATETIME,
        hasgeo TINYINT(1),
        beerid INT)
        """)
    # get beer names and ids
    beersql='''
    SELECT id, ubeername
    FROM beers_unique
    '''
    beerdf=pd.io.sql.read_frame(beersql,con)
    # grab rawtweets
    tweetsql='''
    SELECT *
    FROM rawtweets
    WHERE rawid>%i
    '''%minid
    tweetdf=pd.io.sql.read_frame(tweetsql,con)

# search names double for loop over names and tweets
for beerind,beerrow in beerdf.iterrows():
    # create strings to search against from beer names
    beern=beerrow['ubeername']
    beerid=beerrow['id']
    # make lower
    beern=beern.lower().strip()
    searchstrs=[beern]
    # try concatenating
    if len(beern.split())>1:
        searchstrs.append(beern.replace(' ','').strip())
    # try removing anything in ()
    if len(beern.split('('))>2:
        searchstrs.append(beern.split('(')[0].strip())
    # try substituting a few terms (this is a little biased and kludgy)
    if beern.find('india pale ale')>0:
        searchstrs.append(beern.replace('india pale ale','ipa'))
    if beern.find('extra special bitter')>0:
        searchstrs.append(beern.replace('extra special bitter','esb'))
    # more?????
    
    for twind,twrow in tweetdf.iterrows():
        # pull text of tweet
        tweettext = twrow['tweettext']
        hasmatch=False
        for s in searchstrs:
            # search against text of tweet, find terms in any order
            if np.product([substr in tweettext for substr in s.split()])>0:
                #if tweettext.find(s)>0: # has a match
                hasmatch=True
                print 'found %s in %s'%(s,tweettext)
                break # if true then we're done
        # if there are any matches add data to proctweets adding beer id
        if hasmatch:
            with con:
                # create table for processed tweets
                cur=con.cursor()
                proctwsql="""
                INSERT INTO processedtweets (
                rawid,tweetid,tweetloc,tweettext,tweettime,hasgeo,beerid)
                VALUES (
                %s,%s,%s,%s,%s,%s,%s)
                """
                insertlist=[twrow['rawid'],twrow['tweetid'],twrow['tweetloc'],\
                    twrow['tweettext'],twrow['tweettime'],twrow['hasgeo'],beerid]
                cur.execute(proctwsql,insertlist)
        # update minid for future runs
        minid=twrow['rawid']
        # end tweet loop
        
    #end beer name loop

# save out minid value for future use
with open('rawtweetprocid.txt','w') as f:
    minidstr=str(minid)
    f.write(minidstr)

print 'Done'         

