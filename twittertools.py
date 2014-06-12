'''
twitter tools
'''

import pandas as pd
import tweepy
import numpy as np
import time
from authent import twitauth


apikey=twitauth['apikey']
apikeysecret=twitauth['apikeysecret']
token=twitauth['token']
tokensecret=twitauth['tokensecret']

# authenticate to API
auth=tweepy.OAuthHandler(apikey, apikeysecret)
auth.set_access_token(token, tokensecret)

twitAPI=tweepy.API(auth)

#usboundbox='-125.0011, 24.9493, -66.9326, 49.5904'

def parseTweet(tweet):
    # parse text, time, location from tweet into dict
    if tweet.place:
        place=tweet.place.full_name
    else:
        place=None
    pt= {'id':tweet.id,'text':tweet.text,'time':tweet.created_at,'place':place,\
    'name':tweet.user.name,'userloc':tweet.user.location}
    return pt

def TwitSearch(keywords,API=twitAPI,searchopts={'lang':'en'}):
    # search twitter for keywords through full timeline available
    searchresult = API.search(q=keywords,count=100,**searchopts)
    parsedresults=[parseTweet(x) for x in searchresult]
    print 'Searching for %s'%keywords
    if len(parsedresults)<100: # not even 100 results, so return
        print 'Found %i results'%len(parsedresults)
        if len(parsedresults)>0:
            print 'Last tweet at %s'%parsedresults[-1]['time']
        time.sleep(5.1)
        return parsedresults
    else:
        maxdepth=1000
        
        while True:
            try:
                nextresults=searchresult.next_results
                print nextresults
                kwargs= dict([kv.split('=') for kv in nextresults[1:].split('&')])
                print 'still digging...'
            except:
                print 'Out of results'
                time.sleep(5.1)
                break
            # update keyword arguments for next round of searches
            
            searchresult = API.search(**kwargs)
            print 'Found %i more results'%len(searchresult)
            parsedresults+=[parseTweet(x) for x in searchresult]
            if len(parsedresults)>maxdepth:
                break
            time.sleep(5.1)
        print 'Oldest tweet at %s'%parsedresults[-1]['time']
        print 'Found %i results'%len(parsedresults)
        return parsedresults

    
class StreamLogger(tweepy.StreamListener):
    # pipeline for processing streams from twitter to mySQL
    def __init__(self,dbcon):
        tweepy.StreamListener.__init__(self)
        self.dbcon=dbcon
        self.currid=np.int(time.time()*10000)
    def on_status(self,status):
        # geofilter and save to database
        try:
            if status.place:
                # hack to check if in format city, ST
                if len(status.place.full_name.split(',')[1].strip())==2:
                    print('Geo Tweet text: ' + status.text + status.place.full_name)
                    self.putTweet(self.parseTweet(status,hasgeo=True))
            elif len(status.user.location.split(',')[1].strip())==2: # not an empty string
                print('Tweet text: ' + status.text + status.user.location)
                self.putTweet(self.parseTweet(status,hasgeo=False))
        except:
            print 'Tweet not in correct format'
        return True
    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True # To continue listening
    def on_timeout(self):
        print('Timeout...')
        return True # To continue listening
    
    def parseTweet(self,tweet,hasgeo=False):
        # parse incoming tweet
        if hasgeo:
            pt= {'id':tweet.id,'text':tweet.text.lower().strip().encode('ascii','replace'),'time':tweet.created_at,\
            'place':tweet.place,'geotagged':True}
        else:
            pt= {'id':tweet.id,'text':tweet.text.lower().strip().encode('ascii','replace'),'time':tweet.created_at,\
            'place':tweet.user.location,'geotagged':False}
        return pt
    
    def putTweet(self,parsedtweet):
        # add single tweet to database with timestamp id
        with self.dbcon:
            cur=self.dbcon.cursor()
            sql="""INSERT INTO rawtweets(rawid,tweetid,tweetloc,tweettext,tweettime,hasgeo)
            VALUES(
            %s,%s,%s,%s,%s,%s)
            """
            self.currid+=1
            cur.execute(sql,[self.currid,parsedtweet['id'],parsedtweet['place'],parsedtweet['text'],\
            parsedtweet['time'],parsedtweet['geotagged']])
        return True

def TwitStream(keywords,dbcon,creds=auth):
    # set up and run twitter stream listener
    listener=StreamLogger(dbcon)
    print listener
    stream = tweepy.Stream(creds, listener)
    print 'Starting stream, ctrl-c to exit'
    stream.filter(track=keywords)
    
    