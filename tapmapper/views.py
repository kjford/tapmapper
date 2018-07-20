from flask import render_template, request, jsonify
from tapmapper import app
from helpers.stats import getstatspageinfo
from helpers.similaritymat import get_simdata, output_region_points
import simplejson
from tapmapper.database import session_scope, engine
from tapmapper import models as m


# ROUTING/VIEW FUNCTIONS
@app.route('/')
def index():
    # landing page
    return render_template('map.html')

    
@app.route('/search', methods=['POST'])
def showresults():  
    city = request.form['city']
    with session_scope() as s:
        q = (s.query(m.Beer.beername.label('name'),
                     m.Brewer.brewername.label('brewer'),
                     m.Brewer.location.label('location'),
                     m.Tfidf.TFIDF.label('tfidf'),
                     m.Revstat.avgoverall.label('rating'),
                     m.Beer.id.label('beerid'),
                     m.Beer.brewerid.label('brewerid'),
                     m.CityRegion.locbin_id.label('regionid'))
             .join(m.Brewer, m.Beer.brewerid == m.Brewer.brewerid)
             .join(m.Tfidf, m.Tfidf.beerid == m.Beer.id)
             .join(m.Revstat, m.Revstat.id == m.Beer.id)
             .join(m.CityRegion, m.CityRegion.locbin_id == m.Tfidf.locbinid)
             .join(m.Uscity, m.Uscity.cityid == m.CityRegion.city_id)
             .filter(m.Uscity.fullname == city)
             .order_by(m.Tfidf.TFIDF.desc())
             .limit(5)
        )
        data = [x._asdict() for x in q]

    var_dict = {"city": city}
    # Add data to dictionary
    var_dict["data"] = data
    # get similarity data
    if data:
        simdata = get_simdata(data[0]["regionid"])
    else:
        simdata = []
    var_dict["simdata"] = simdata
    return jsonify(var_dict)


@app.route('/beercount',methods=['GET'])
def showcountmap():
    output = {}
    output['data'] = output_region_points()
    return jsonify(output)


@app.route('/poplist',methods=['GET'])
def poplist():
    output = dict()
    with session_scope() as s:
        q = (s.query(m.Uscity.fullname)
             .join(m.Procbintweet, m.Procbintweet.cityid == m.Uscity.cityid)
             .distinct()
             )
        citylist = [x.fullname for x in q]
    output['data'] = citylist
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
    output = dict()
    jfile = './tapmapper/static/snob.json'
    fobj = open(jfile)
    jobj = simplejson.load(fobj)
    fobj.close()
    data = getstatspageinfo(engine, jobj)
    output['rawcount'] = data['rawcount']
    output['data'] = data['data']
    return render_template('stats.html', settings=output)


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500
