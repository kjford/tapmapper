# create a new beers table that adds part of brewery name to beer names
import pandas as pd
import numpy as np
import pymysql as mdb
from authent import dbauth as authsql

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
    SELECT beers.id, beers.beername, brewers.brewername
    FROM beers, brewers
    WHERE beers.brewerid=brewers.brewerid
    '''
    beerdf=pd.io.sql.read_frame(qry,con)
print 'Processing %i entries'%len(beerdf)
# determine beer names that are not unique
ids=[]
unames=[]
for bn,gr in beerdf.groupby('beername'):
    # kill quotes on beer names
    bn=bn.replace('"','').strip()
    if len(gr)>1 or len(bn)<4: # not unique or name too short
        for i in gr.iterrows():
            # stem brewery name to get rid of everything after 'brew'
            breweryname=i[1]['brewername']
            # if the name is not unique and there is no brewery info, it's useless
            if len(breweryname)>2:
                # get rid of 'The' if it is there
                breweryname=breweryname.replace('The','').strip()
                brewwernameshort=breweryname.split('Brew')[0].strip()
                newname=brewwernameshort+' '+bn
                #print 'switching %s from %s to %s'%(bn,breweryname,newname)
                unames.append(newname)
                ids.append(int(i[1]['id']))
    else:
        # looks ok
        unames.append(bn)
        ids.append(int(gr['id']))

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
    vals = zip(ids,unames)
    cur.executemany(instertsql,vals)
print 'done'
        
