'''
beer bong: twitter beer stream to mysql db
'''
import pymysql as mdb
import twittertools
from authent import dbauth as authsql


# Create table to hold the tweets before processing

con=mdb.connect(**authsql)
with con:
    cur=con.cursor()
    #cur.execute("""DROP TABLE IF EXISTS rawtweets;""")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS rawtweets(
        rawid BIGINT NOT NULL PRIMARY KEY,
        tweetid BIGINT, 
        tweetloc VARCHAR(150),
        tweettext TEXT,
        tweettime DATETIME,
        hasgeo TINYINT(1))
        """)
    
# note: connection closed, need to reopen for writing

# start a twitter stream
keywords=['drinking','ale','beer','tap','ipa','stout','imperial'] # from top 50 minus stopwords

stillgoing = True
counter = 0
while stillgoing:
    try:
        twittertools.TwitStream(keywords,con)
    except:
        print 'Connection fail. Sleeping.'
        time.sleep(10)
        counter += 1
        if counter > 10:
            stillgoing = False