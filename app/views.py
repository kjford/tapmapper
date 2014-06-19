from flask import render_template,url_for,request,jsonify
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db, query_db
from app.helpers.similaritymat import getSimdata

import jinja2


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


@app.route('/slides')
def about():
    # Renders slides.html.
    return render_template('slides.html')

@app.route('/author')
def contact():
    # Renders author.html.
    return render_template('author.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
