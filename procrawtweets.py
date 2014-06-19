'''
process raw tweets:
search each raw tweet across beer names and beer name variants
associate tweets with beer name id if found
add to processedtweets table (create if doesn't exist)
'''

import pandas as pd
import pymysql as mdb
import numpy as np
import string
from authent import dbauth as authsql

# clunky hack that needs work:
# start processing mysql data base from id >= minid
with open('rawtweetprocid.cfg','r') as f:
    minid=int(f.read())
print 'Loading data'
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
        beerid INT,
        cityid INT)
        """)
    # get beer names and ids
    beersql='''
    SELECT b.id, b.ubeername, r.nreviews
    FROM beers_unique AS b
    JOIN revstats AS r
    ON b.id=r.id
    '''
    beerdf=pd.io.sql.read_frame(beersql,con)
    # grab rawtweets
    tweetsql='''
    SELECT *
    FROM rawtweets
    WHERE rawid>%i
    '''%minid
    tweetdf=pd.io.sql.read_frame(tweetsql,con)
    # get us cities
    citysql='''
    SELECT cityid, fullname
    FROM uscities
    '''
    citydf = pd.io.sql.read_frame(citysql,con)
    citylist=citydf.fullname.apply(lambda(x): x.lower()).tolist()
print 'Start from index %i'%minid
# for getting rid of punctuation
replacerstr=string.maketrans(string.punctuation, ' '*len(string.punctuation))

'''
below has been moved to the rename_beers script
# try removing anything in ()
beerdf['ubeername']=beerdf['ubeername'].apply(lambda(x):x.split('(')[0])
# make lower and remove punctuation
beerdf['ubeername']=beerdf['ubeername'].apply(lambda(x):x.translate(replacerstr).lower().strip())
# try substituting a few terms (this is a little biased and kludgy)
beerdf['ubeername']=beerdf['ubeername'].apply(lambda(x):x.replace('india pale ale','ipa'))
beerdf['ubeername']=beerdf['ubeername'].apply(lambda(x):x.replace('extra special bitter','esb'))
'''

# add column of string lengths
beerdf['namelen']=beerdf.ubeername.apply(len)
# sort beerdf by length of name string then number of nreviews
beerdf=beerdf.sort(['namelen','nreviews'],ascending=[0,0])

# create massive tweet of all tweets padded to 200 characters and squished
print 'Making super tweet for quicker searching'
supertweet=''
tid=[]
for twind,twrow in tweetdf.iterrows():
    tid.append(twind)
    tw=twrow['tweettext']
    l=len(tw)
    tw=tw+' '*(200-l)
    supertweet+=tw


supertweet=supertweet.translate(replacerstr).lower()
print 'Super tweet is %i characters'%len(supertweet)

print 'Seaching tweets for each beer name'
nbeers=len(beerdf)
count=1
# search names: for loop over names
for beerind,beerrow in beerdf.iterrows():
    # create strings to search against from beer names
    beern=beerrow['ubeername']
    beerid=beerrow['id']
    print '%s: %i of %i'%(beern,count,nbeers)
    count+=1
    # find all instances of full term
    searching=0
    if len(beern)>3:  
        while True:
            searching=supertweet.find(beern,searching+1)
            if searching > -1:
                # found, actual index of tweet is:
                twindact=searching/200 #this is a floored integer
                # make the location tag more consistent
                rawloc=tweetdf['tweetloc'][twindact].lower().strip()
                loc=rawloc.split(',')[0].strip() + ', '+rawloc.split(',')[1].strip()
                # parse against us cities database
                if loc in citylist:
                    ci=int(citydf.cityid[citylist.index(loc)])
                else:
                    ci=None
                with con:
                    # create table for processed tweets
                    cur=con.cursor()
                    proctwsql="""
                    INSERT INTO processedtweets (
                    rawid,tweetid,tweetloc,tweettext,tweettime,hasgeo,beerid,cityid)
                    VALUES (
                    %s,%s,%s,%s,%s,%s,%s,%s)
                    """
                    insertlist=[int(tweetdf['rawid'][twindact]),int(tweetdf['tweetid'][twindact]),\
                            loc,tweetdf['tweettext'][twindact],\
                            tweetdf['tweettime'][twindact].to_datetime(),\
                            int(tweetdf['hasgeo'][twindact]),beerid,ci]
                    cur.execute(proctwsql,insertlist)
            else:
                break
        # replace all instance with spaces
        supertweet=supertweet.replace(beern,' '*len(beern))
        
#end beer name loop
minid=tweetdf['rawid'].max()

# save out minid value for future use
with open('rawtweetprocid.cfg','w') as f:
    minidstr=str(minid)
    f.write(minidstr)

print 'Done'         

