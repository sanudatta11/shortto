import os
import re
import requests
import validators
from flask import json
from flask import make_response, jsonify
from flask import render_template, flash, redirect, request,session
from flask import send_from_directory
from flask import url_for
from werkzeug.security import safe_str_cmp

from app import app, db,limiter
from app.models import Shortto,Client_auth, api_auth
from app.forms import Url_form
from app.helper import idtoshort_url
from config import blacklist
from flask_restful import Resource, Api
from flask_jwt import JWT, jwt_required
from flask_jwt_extended import (
    JWTManager, jwt_required, create_access_token,
    get_jwt_identity
)

@app.route('/api/v1/login',methods=['POST'])
@app.route('/api/v1/login/',methods=['POST'])
@limiter.limit("1000 per day")
def api_auth_function():
    if not request.is_json:
        return jsonify({"msg": "Missing JSON in request"}), 400
    client_id = request.json.get('client_id', None)
    client_secret = request.json.get('client_secret', None)

    if not client_id:
        return jsonify({"msg": "Missing client_id parameter"}), 400
    if not client_secret:
        return jsonify({"msg": "Missing client_secret parameter"}), 400
    
    if not (api_auth.query.filter_by(client_id=client_id,client_secret=client_secret).count() > 0):
        return jsonify({"msg": "Bad Client id or Client Secret"}), 401

    #Identity is made as Client Secret as it is unique
    access_token = create_access_token(identity=client_secret)
    return jsonify(access_token=access_token), 200

@app.route('/api/v1/create_url',methods=['POST'])
@app.route('/api/v1/create_url/',methods=['POST'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_secret = get_jwt_identity()

    long_url = request.form['long_url']

    return jsonify(test=long_url,code=322), 200

    for url_s in blacklist:
        url_s_1 = '://' + url_s
        url_s_2 = 'www.' + url_s
        if (url_s_1 in (long_url).lower()) or (url_s_2 in (long_url).lower()):
            return jsonify(code=430,error="Blacklist URL Request",message="The URL you entered to shorten is Blacklisted")

    if not validators.url(long_url):
        return jsonify(code=510,error="Invalid URL",message="The Long URL you entered is Invalid!")
    
    
    if request.form['short_url']:
        short_url = request.form['short_url']

        if not re.match("^[A-Za-z0-9-]+$", short_url):
            return jsonify(code=520,error="Invalid URL Request",message="The Shortened URL character you entered is invalid")

            # Check if unique or not
        if Shortto.query.filter_by(short_url=request.form['to_url']).count() > 0:
        # Already Used Short Url
           return jsonify(code=320,error="Short URL Already Used",message="Please select another short URL")

        temp = Shortto(big_url=long_url, short_url=short_url)
        db.session.add(temp)
        db.session.commit()

        return jsonify(code=200,error="None",message="Short URL is made",url=app.config['BASE_URL']+short_url)
    else:
        rows = Shortto.query.count()
        rows = int(rows)
        rows += 1
        short_url = idtoshort_url(int(rows))
        while Shortto.query.filter_by(short_url=short_url).count() > 0:
            rows += 1
            short_url = idtoshort_url(rows)
        temp = Shortto(big_url=request.form['from_url'], short_url=short_url)
        db.session.add(temp)
        db.session.commit()

        return jsonify(code=200, error="None", message="Short URL is made", url=app.config['BASE_URL'] + short_url)

@app.route('/url/self',methods=['GET'])
@app.route('/url/self/',methods=['GET'])
@limiter.exempt
def self_urls():
    prev_url = request.cookies.get('__shortto__')
    prev_url_list = []
    send_list = []
    if prev_url:
        prev_url_list = prev_url.split('#')
    for items in prev_url_list:
        temp_list = []
        temp = Shortto.query.filter_by(short_url=items).first()
        if temp is not None:
            temp_list.append(temp.big_url)
            temp_list.append(items)
            temp_list.append(temp.clicks)
            send_list.append(temp_list)
    return render_template('analytics.html',prev_url_list=send_list)

@app.route('/make/url')
@app.route('/make/url/')
@limiter.exempt
def index2():
    return render_template('index.html')

@app.route('/url/done',methods=['GET'])
@app.route('/url/done/',methods=['GET'])
@limiter.exempt
def short_done():
    resp = make_response(render_template('done.html', code=200, short_url=app.config['BASE_URL'] + request.args.get('short_url')))
    prev_url = request.cookies.get('__shortto__')
    prev_url_list = []
    if prev_url:
        prev_url_list = prev_url.split('#')
    prev_url_list.append(request.args.get('short_url'))
    prev_url = '#'.join(prev_url_list)
    resp.set_cookie('__shortto__',prev_url)
    return resp

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@limiter.exempt
def index():
    form = Url_form(request.form)
    tot_urls = Shortto.query.count()
    tot_clicks_obj = db.session.query(Shortto, db.func.sum(Shortto.clicks))
    tot_clicks = tot_clicks_obj[0][1]
    if request.method == 'POST' and request.form['from_url']:

        # Recaptcha Verify

        g_captcha_response = request.form['g-recaptcha-response']
        data = {'secret': '6LeFWDYUAAAAAAP1FaIZ8Q6NtJxHO9n3Sa1l6RKu', 'response': g_captcha_response,'remoteip': request.remote_addr}
        post_obj = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)

        if post_obj.status_code == 200:
            #All Fine
            json_data = json.loads(post_obj.text)
            if json_data['success'] == True:
                #Passed
                done = True
            else:
                return redirect(url_for('index2',error_code=str(json_data['error-codes'][0])))
        else:
                return redirect('/',320)
        # Recaptcha End
        for url_s in blacklist:
            url_s_1 = '://' + url_s
            url_s_2 = 'www.' + url_s
            if (url_s_1 in (request.form['from_url']).lower()) or (url_s_2 in (request.form['from_url']).lower()):
                return render_template('index.html', blacklist_url=True, tot_clicks=tot_clicks, tot_urls=tot_urls)

        if not validators.url(request.form['from_url']):
            return render_template('index.html', url_error=True, tot_clicks=tot_clicks, tot_urls=tot_urls)

        if request.form['to_url']:

            if not re.match("^[A-Za-z0-9-]+$",request.form['to_url']):
                return render_template('index.html', code=320, error_url_type=True, tot_clicks=tot_clicks,
                                       tot_urls=tot_urls)

            # Check if unique or not
            if Shortto.query.filter_by(short_url=request.form['to_url']).count() > 0:
                # Already Used Short Url
                error_url = True
                return render_template('index.html', code=320, error_url=error_url,tot_clicks=tot_clicks, tot_urls=tot_urls)

            short_url = request.form['to_url']

            # Url Not Present
            temp = Shortto(big_url=request.form['from_url'], short_url=request.form['to_url'])
            db.session.add(temp)
            db.session.commit()
            return redirect(url_for('short_done', short_url=short_url))
        else:
            rows = Shortto.query.count()
            rows = int(rows)
            rows+=1
            short_url = idtoshort_url(int(rows))
            while Shortto.query.filter_by(short_url=short_url).count() > 0:
                rows+=1
                short_url = idtoshort_url(rows)
            temp = Shortto(big_url=request.form['from_url'], short_url=short_url)
            db.session.add(temp)
            db.session.commit()
            # prev_url_data = request.cookies.get(COOKIE_VAR)
            # prev_url_data_split = []
            # if prev_url_data:
            #     prev_url_data_split = prev_url_data.split('#')
                # THis variable has previous data
            return redirect(url_for('short_done',short_url=short_url))
            # resp.set_cookie(COOKIE_VAR, '#'.join(prev_url_data_split))

    # Just Index Render get analytics data
    return render_template('index.html', form=form, tot_clicks=tot_clicks, tot_urls=tot_urls)


@app.route('/<string:short_data>', methods=['GET'])
@app.route('/<string:short_data>/', methods=['GET'])
@limiter.exempt
def routeit(short_data):
    temp = Shortto.query.filter_by(short_url=short_data).first()
    if temp is not None:
        temp.clicks += 1
        db.session.commit()
        url = temp.big_url
        if not validators.url(url):
            return render_template('index.html',url_error=True)
        return redirect(url, code=302)
    return render_template('notfound.html')

@app.route('/favicon.ico')
@limiter.exempt
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
@limiter.exempt
def not_found(error):
    return render_template('error404.html') , 404


@app.errorhandler(500)
@limiter.exempt
def not_found(error):
    return render_template('error500.html'), 500
