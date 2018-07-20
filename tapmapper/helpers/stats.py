"""
This needs some refactoring:
Cache results
Switch to ORM
"""

def getstatspageinfo(eng, cacheddata):
    # get all the data for the stats page
    with eng.connect() as cur:
        # count of raw tweets
        rawcnt = list(cur.execute("""
            SELECT COUNT(*)
            FROM rawtweets;
            """))[0][0]

        # cities with most beer tweets
        topcities = list(cur.execute("""
            SELECT DISTINCT(l.fullname)
            FROM processedtweets as p
            JOIN uscities as l
            ON l.cityid=p.cityid
            WHERE p.cityid IS NOT NULL
            GROUP BY p.cityid
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """))

        # top beers
        topbeers = list(cur.execute("""
            SELECT b.beername
            FROM beers as b
            JOIN procbintweets as p
            ON p.beerid=b.id
            GROUP BY p.beerid
            ORDER BY COUNT(*) DESC
            LIMIT 5
            """))
        cur.close()
    data = dict()
    data['rawcount'] = rawcnt
    data['data'] = []
    n = len(topcities)  # this should be 5
    # get cached snob rankings
    topsnob = cacheddata[-n:][::-1]
    bottomsnob = cacheddata[:n]
    for i in xrange(n):
        data['data'].append(
            {'snobs': topsnob[i],
             'lowbrows': bottomsnob[i],
             'topcities': topcities[i][0].decode('latin-1','ignore'),
             'topbeers': topbeers[i][0].decode('latin-1','ignore')})
     
    return data
