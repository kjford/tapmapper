from flask import render_template,url_for,request,jsonify
from tapmapper import app
from helpers.database import con_db, query_db, getcitylist, getstatspageinfo
from helpers.similaritymat import getSimdata,outputRegionPoints
import simplejson
import jinja2

# DATABASE SETTINGS
host = app.config["DATABASE_HOST"]
port = app.config["DATABASE_PORT"]
user = app.config["DATABASE_USER"]
passwd = app.config["DATABASE_PASSWORD"]
db = app.config["DATABASE_DB"]


# ROUTING/VIEW FUNCTIONS
@app.route('/')
def index():
    # landing page
    return render_template('map.html')
    
@app.route('/search', methods=['POST'])
def showresults():  
    city = request.form['city'];
    con = con_db(host, port, user, passwd, db)
    var_dict = {
        "city": city
    }
    # Query the database
    data = query_db(con, var_dict)
    # Add data to dictionary
    var_dict["data"] = data
    # get similarity data
    if data:
        simdata= getSimdata(con,data[0]["regionid"])
    else:
        simdata=[]
    var_dict["simdata"]=simdata
    return jsonify(var_dict)

@app.route('/beercount',methods=['GET'])
def showcountmap():
    con = con_db(host, port, user, passwd, db)
    output={}
    output['data']=outputRegionPoints(con)
    return jsonify(output)

@app.route('/poplist',methods=['GET'])
def poplist():
    con = con_db(host, port, user, passwd, db)
    output={}
    output['data']=getcitylist(con)
    return jsonify(output)
      
@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.route('/stats', methods=['GET'])
def stats():
    con = con_db(host, port, user, passwd, db)
    output={}
    jfile='./app/static/snob.json'
    fobj=open(jfile)
    jobj=simplejson.load(fobj)
    fobj.close()
    data=getstatspageinfo(con,jobj)
    output['rawcount']=data['rawcount']
    output['data']=data['data']
    return render_template('stats.html',settings=output)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
