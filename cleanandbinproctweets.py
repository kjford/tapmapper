'''
clean and location bin processed tweets:
get tweets with location ids
remove blacklist beer ids (non-specific/common word beer names)
bin locations by proximity/#tweets
add to procbintweets table (drop and create)
'''

import pandas as pd
import pymysql as mdb
import numpy as np
from authent import dbauth as authsql
from blacklist import blacklist

# minimum number of tweets in a city - old
mintweets=10 # this should probably change as I get more data
# use this instead:
# compute max number of cities to use, using ones with most tweets
maxcities = 200

con=mdb.connect(**authsql)
with con:
    # load processed tweets that have cityid
    twsql='''
    SELECT p.proctwid,p.beerid,p.cityid,l.lat,l.lng,l.fullname
    FROM processedtweets as p
    JOIN uscities as l
    ON l.cityid=p.cityid
    WHERE p.cityid IS NOT NULL
    '''
    twdf=pd.io.sql.read_frame(twsql,con)
    # drop and create table procbintweets
    cur=con.cursor()
    cur.execute("""DROP TABLE IF EXISTS procbintweets;""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS procbintweets(
        procbinid INT AUTO_INCREMENT PRIMARY KEY,
        proctweetid INT, 
        beerid INT,
        cityid INT,
        locbinid INT
        )
        """)

# remove id's in blacklist
keepinds = [x[0] for x in twdf.iterrows() if x[1]['beerid'] not in blacklist]
twdf=twdf.ix[keepinds]

'''create similarity matrix'''

# for computing distance from lat and lng
def distcalc(lat1,lng1,lat2,lng2):
    # do this the dirty way
    d=np.sqrt((lat1-lat2)**2 + (lng1-lng2)**2)
    # degree to rad
    lat1r= np.pi *lat1/180.0
    lat2r= np.pi *lat2/180.0
    lng1r= np.pi *lng1/180.0
    lng2r= np.pi *lng1/180.0
    # distance in units of sphere radius
    #d=np.arccos(np.sin(lat1r) * np.sin(lat2r) + np.cos(lat1r) * np.cos(lat2r) * np.cos(lng2r-lng1r))
    #return d*3863.191 # in miles
    return d


# get counts in each city and lat and lng
# hold cityid, count of total tweets, lat and long
cid=[]
ntweets=[]
latcity=[]
lngcity=[]
for cityid, groupdata in twdf.groupby('cityid'):
    cid.append(cityid)
    ntweets.append(int(len(groupdata)))
    if len(groupdata)>1:
        latcity.append(np.float(groupdata['lat'].values[0]))
        lngcity.append(np.float(groupdata['lng'].values[0]))
    else:
        latcity.append(np.float(groupdata['lat']))
        lngcity.append(np.float(groupdata['lng']))

# reorder
cid=np.array(cid)
regionid=np.arange(len(cid))
ntweetsarr=np.array(ntweets)
latcity=np.array(latcity)
lngcity=np.array(lngcity)
# process largest cities first
reordered=ntweetsarr.argsort()[::-1]
ntweetsarr.sort()
ntweetsarr=ntweetsarr[::-1]
latcity=latcity[reordered]
lngcity=lngcity[reordered]
cid=cid[reordered]

#print ntweetsarr[0],ntweetsarr[-1]
# make similarity matrix = distance between cities
print 'Building distance matrix'
simarray=np.zeros((len(cid),len(cid)))
for c1 in xrange(len(cid)):
    for c2 in xrange(0,c1):
        dact= distcalc(latcity[c1],lngcity[c1],latcity[c2],lngcity[c2])
        simarray[c1,c2]=dact 
        simarray[c2,c1]=dact

# determine mintweets from the number of tweets array
if len(ntweetsarr)>maxcities:
    mintweets = ntweetsarr[maxcities]
else:
    mintweets=10

# if a city has < mintweets, add to closest city above threshold
for i in xrange(len(cid)):
    if ntweetsarr[i]>=mintweets: # meets criteria
        pass # region id is city id
    else:
        # for cities close to i
        sorteddist=simarray[i,:].argsort()
        #print sorteddist[1],sorteddist[-1]
        j=1
        while True:
           lookingat = regionid[sorteddist[j]]
           if ntweetsarr[sorteddist[j]]>mintweets:
               # add to region
               regionid[i]=lookingat
               break
           j+=1


# reassign labels of regions to each tweet/beer
print 'Assigning region ids'
pid=[] #proctweetid
bid=[] #beerid
allcid=[] # cityid
allrid=[] # regionid
for beertw in twdf.iterrows():
    pid.append(int(beertw[1]['proctwid']))
    bid.append(int(beertw[1]['beerid']))
    thiscity=beertw[1]['cityid']
    allcid.append(int(thiscity))
    thisregion=regionid[cid==thiscity][0]
    allrid.append(int(thisregion))
    

# output to db

with con:
    addtosql='''
    INSERT INTO procbintweets
    (proctweetid,beerid,cityid,locbinid)
    VALUES (
    %s,%s,%s,%s)
    '''
    vals=zip(pid,bid,allcid,allrid)
    cur=con.cursor()
    cur.executemany(addtosql,vals)

print 'Done'
    