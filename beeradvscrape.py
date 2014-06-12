'''
(Gently) Scrape BeerAdvocate for their brewery names
from id tags
'''
import pandas as pd
import cPickle
#import MySQLdb as mdb
import pymysql as mdb
import time
from bs4 import BeautifulSoup
import urllib2
import sys
from authent import dbauth as auth

# get brewery ids from database

sql='''
    SELECT DISTINCT beer_brewerid
    FROM RateBeer
    '''

con=mdb.connect(**auth)
print 'Loading brewery ids'
df=pd.io.sql.read_frame(sql,con)
brewerids=list(df['beer_brewerid'])
print 'Found %i brewery ids'%len(brewerids)

# pull info from beeradvocate
baseurl='http://www.beeradvocate.com/beer/profile/'
waittime=2.0 #seconds
# hold brewery names and locations
breweries=[]
locations=[]
count=0
for bid in brewerids:
    print 'Finding id# %i'%bid
    url=baseurl+str(bid)
    try:
        req=urllib2.Request(url,headers={'User-Agent':'Magic Browser'})
        html=urllib2.urlopen(req).read()
        soup=BeautifulSoup(html,'lxml')
        brewerinfo=str(soup.find('title'))[7:] #get rid of "<title>" tag
        brewername=brewerinfo.split('|')[0]
        loc=brewerinfo.split('|')[1]
        breweries.append(brewername)
        locations.append(loc)
        print brewername+' : '+loc
    except:
        e=sys.exc_info()[0]
        print 'Error on id %i (count=%i): %s'%(bid,count,e)
        breweries.append('')
        locations.append('')
    time.sleep(waittime)
    count+=1
print ('Done. Saving.')

# save s a dictionary
brewdict={'id':brewerids,'brewer':breweries,'location':locations}
cPickle.dump(brewdict,open('breweries.cpk','w'))
        
    