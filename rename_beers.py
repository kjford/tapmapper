# create a new beers table that adds part of brewery name to beer names
import pandas as pd
import numpy as np
import pymysql as mdb
import string
from authent import dbauth as authsql


# important variable: how many reviews does a beer need to be included
minreviews=50

con=mdb.connect(**authsql)
print 'Grabbing data and creating database'
with con:
    cur=con.cursor()
    # make the table for unique beer names
    #cur.execute("""DROP TABLE IF EXISTS beers_unique;""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS beers_unique (
        id INT NOT NULL PRIMARY KEY,
        ubeername VARCHAR(200)
        )
        """)
    # get all beer names and breweries
    qry='''
    SELECT beers.id, beers.beername, brewers.brewername, revstats.nreviews
    FROM beers
    JOIN brewers ON beers.brewerid=brewers.brewerid
    JOIN revstats ON beers.id=revstats.id
    '''
    beerdf=pd.io.sql.read_frame(qry,con)
print 'Processing %i entries'%len(beerdf)
# determine beer names that are not unique
# strip and munge:
replacerstr=string.maketrans(string.punctuation, ' '*len(string.punctuation))
# removing anything in () taking only string before
beerdf['beername']=beerdf['beername'].apply(lambda(x):x.split('(')[0])
# make lower and remove punctuation
beerdf['beername']=beerdf['beername'].apply(lambda(x):x.translate(replacerstr).lower())
# strip quotes
beerdf['beername']=beerdf['beername'].apply(lambda(x):x.replace('"',''))
# try substituting a few terms (this is a little biased and kludgy)
beerdf['beername']=beerdf['beername'].apply(lambda(x):x.replace('india pale ale','ipa'))
beerdf['beername']=beerdf['beername'].apply(lambda(x):x.replace('extra special bitter','esb'))
# stip leading and tailing white space
beerdf['beername']=beerdf['beername'].apply(lambda(x):x.strip())

# add column of string lengths
beerdf['namelen']=beerdf.beername.apply(len)


ids=[]
unames=[]
# loop through and determine make beer names unique
for bn,gr in beerdf.groupby('beername'):
    
    if len(gr)>1 or len(bn)<4: # not unique or name too short
        for i in gr.iterrows():
            # stem brewery name to get rid of everything after 'brew'
            breweryname=i[1]['brewername'].lower()
            # if the name is not unique and there is no brewery info, it's useless
            if len(breweryname)>2:
                # get rid of 'The' if it is there
                breweryname=breweryname.replace('the','').strip()
                brewernameshort=breweryname.split('brew')[0].strip()
                if len(brewernameshort)>3: # not that useful if the brewer name is too short
                    newname=brewernameshort+' '+bn
                    #print 'switching %s from %s to %s'%(bn,breweryname,newname)
                    if i[1]['nreviews']>=minreviews:
                        unames.append(newname)
                        ids.append(int(i[1]['id']))
    else:
        # looks ok
        #does it meet review number criteria
        if gr['nreviews']>=minreviews:
            unames.append(bn)
            ids.append(int(gr['id']))
# get rid of beers that are words in the top 1000 english words list
wl=pd.read_table('google-10000-english/google-10000-english.txt',header=None)
wl1000=list(wl[0][:1000])

ziplist=zip(ids,unames)

vals=[x for x in ziplist if x[1] not in wl1000]


print 'Found %i (more) unique names'%len(unames)
print 'Adding to database'
with con:
    cur=con.cursor()
    instertsql='''
    INSERT INTO beers_unique (
    id, ubeername)
    VALUES(
    %s,%s)
    '''
    cur.executemany(instertsql,vals)
print 'done'
        
