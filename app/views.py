from flask import render_template,url_for,request,redirect
from app import app, host, port, user, passwd, db
from app.helpers.database import con_db, query_db

import jinja2


# ROUTING/VIEW FUNCTIONS
@app.route('/', methods=['GET'])
def index():
    # Show the start page
    if request.method=='GET':
        return redirect(url_for('showresults'))
    return render_template('searchbar.html')



@app.route('/table', methods=['GET'])
def showresults():
    # Create database connection
    con = con_db(host, port, user, passwd, db)

    var_dict = {
        "city": request.form["city"]
    }

    # Query the database
    data = query_db(con, var_dict)

    # Add data to dictionary
    var_dict["data"] = data

    return render_template('table.html', settings=var_dict)


@app.route('/home')
def home():
    # Renders home.html.
    return render_template('home.html')

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
