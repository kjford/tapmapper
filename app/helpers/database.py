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
    cur = con.cursor()
    cur.execute(
        """
        SELECT b.beername,br.brewername,br.location, a.TFIDF, r.avgoverall
        FROM beers AS b
        JOIN (
            SELECT beerid,TFIDF
            FROM tfidf
            WHERE city='{0}'
        ) AS a 
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

        index["name"] = beer[0]
        index["brewer"] = beer[1]
        index["location"] = beer[2]
        index["tfidf"] = float(json.dumps(beer[3]))
        index["rating"] = float(json.dumps(beer[4]))

        data_array.append(index)

    cur.close()
    con.close()
    return data_array