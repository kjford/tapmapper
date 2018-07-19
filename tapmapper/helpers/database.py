import pymysql
import sys
import simplejson as json


# Returns MySQL database connection
def con_db(host, port, user, passwd, db):
    try:
        con = pymysql.connect(host=host, port=port, user=user, passwd=passwd, db=db)

    except pymysql.Error, e:
        print "Error %d: %s" % (e.args[0], e.args[1])
        sys.exit(1)

    return con

# get data from tfidf database
def query_db(con, dict):
    data_array = []

    # Request args
    search_city = dict["city"]
    
    # Query database
    with con:
        cur = con.cursor()
        cur.execute(
            """
            SELECT b.beername,br.brewername,br.location, a.TFIDF, r.avgoverall,b.id,br.brewerid,reg.region
            FROM (
            SELECT cityid
            FROM uscities
            WHERE fullname LIKE '{0}'
            ) AS us
            JOIN (
            SELECT DISTINCT p.locbinid AS region, p.cityid
            FROM procbintweets AS p
            ) AS reg
            ON reg.cityid=us.cityid
            JOIN tfidf AS a
            ON reg.region=a.locbinid
            JOIN beers AS b
            ON a.beerid=b.id
            JOIN brewers AS br
            ON b.brewerid=br.brewerid
            JOIN revstats AS r
            ON b.id=r.id    
            ORDER by a.TFIDF DESC
            LIMIT 5
            """.format(search_city)
        )

        data = cur.fetchall()
        for beer in data:
            index = {}

            index["name"] = beer[0].decode('latin-1','ignore')
            index["brewer"] = beer[1].decode('latin-1','ignore')
            index["location"] = beer[2].decode('latin-1','ignore')
            index["tfidf"] = json.dumps(beer[3])
            index["rating"] = json.dumps(beer[4])
            index["beerid"] = beer[5]
            index["brewerid"] = beer[6]
            index["regionid"] = beer[7]
            data_array.append(index)

        cur.close()
    return data_array

def getcitylist(con):
    # git current list of all cities that have tweets to populate search bar
    with con:
        cur = con.cursor()
        cur.execute('''
        SELECT distinct(l.fullname)
        FROM processedtweets as p
        JOIN uscities as l
        ON l.cityid=p.cityid
        WHERE p.cityid IS NOT NULL
        ''')
        data=cur.fetchall()
        dataarray=[]
        for city in data:
            dataarray.append(city[0].decode('latin-1','ignore'))
        cur.close()
    return dataarray


def getstatspageinfo(con,cacheddata):
    # get all the data for the stats page
    with con:
        # count of raw tweets
        cur = con.cursor()
        cur.execute('''
        SELECT COUNT(*)
        FROM rawtweets
        ''')
        rawcnt=cur.fetchall()[0][0]
        # cities with most beer tweets
        cur.execute('''
        SELECT DISTINCT(l.fullname)
        FROM processedtweets as p
        JOIN uscities as l
        ON l.cityid=p.cityid
        WHERE p.cityid IS NOT NULL
        GROUP BY p.cityid
        ORDER BY COUNT(*) DESC
        LIMIT 5
        ''')
        topcities=cur.fetchall()
        # top beers
        cur.execute('''
        SELECT b.beername
        FROM beers as b
        JOIN procbintweets as p
        ON p.beerid=b.id
        GROUP BY p.beerid
        ORDER BY COUNT(*) DESC
        LIMIT 5
        '''
        )
        topbeers=cur.fetchall()
        cur.close()
    data={}
    data['rawcount']=rawcnt
    data['data']=[]
    n=len(topcities) #this should be 5
    # get cached snob rankings
    topsnob=cacheddata[-n:][::-1]
    bottomsnob=cacheddata[:n]
    for i in xrange(n):
        data['data'].append({'snobs':topsnob[i],'lowbrows':bottomsnob[i],'topcities':topcities[i][0].decode('latin-1','ignore'),'topbeers':topbeers[i][0].decode('latin-1','ignore')})
     
    return data
        
        