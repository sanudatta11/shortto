import os
import re
import requests
import validators
from flask_cors import CORS, cross_origin
import sys
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

# @app.route('/url/done',methods=['GET'])
# @app.route('/url/done/',methods=['GET'])
# @limiter.exempt
# def short_done():
#     resp = make_response(render_template('done.html', code=200, short_url=app.config['BASE_URL'] + request.args.get('short_url')))
#     prev_url = request.cookies.get('__shortto__')
#     prev_url_list = []
#     if prev_url:
#         prev_url_list = prev_url.split('#')
#     prev_url_list.append(request.args.get('short_url'))
#     prev_url = '#'.join(prev_url_list)
#     resp.set_cookie('__shortto__',prev_url)
#     return resp

# Test Routes for New UI

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@limiter.exempt
def index():
    tot_urls = Shortto.query.count()
    tot_clicks_obj = db.session.query(Shortto, db.func.sum(Shortto.clicks))
    tot_clicks = tot_clicks_obj[0][1]
    return render_template('index.html', tot_clicks=tot_clicks, tot_urls=tot_urls)

@app.route('/dashboard', methods=['GET'])
@limiter.exempt
def dashboard():
    return render_template('dashboard.html')

@app.route('/self/terms', methods=['GET'])
@app.route('/self/terms/', methods=['GET'])
@limiter.exempt
def terms():
    return render_template('terms.html')

@app.route('/self/policy', methods=['GET'])
@app.route('/self/policy/', methods=['GET'])
@limiter.exempt
def policy():
    return render_template('gdpr.html')

@app.route('/login', methods=['GET'])
@app.route('/login/', methods=['GET'])
@limiter.exempt
def login():
    return render_template('login.html')

@app.route('/register', methods=['GET'])
@app.route('/register/', methods=['GET'])
@limiter.exempt
def register():
    return render_template('register.html')

# End of Test Routes for new UI

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
