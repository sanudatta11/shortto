import os
import re
import requests
import validators
from flask import json
from flask import make_response, jsonify
from flask import render_template, flash, redirect, request,session
from flask import send_from_directory
from flask import url_for

from app import app, db
from app.models import Shortto
from sqlalchemy import func
from app.forms import Url_form, Login
from app.helper import idtoshort_url
from flask_wtf.csrf import CSRFError
from sqlalchemy.sql import func
from config import blacklist

@app.route("/get_my_ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200

@app.route('/url/self',methods=['GET'])
@app.route('/url/self/',methods=['GET'])
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
def index2():
    return render_template('index.html')

@app.route('/url/done',methods=['GET'])
@app.route('/url/done/',methods=['GET'])
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
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.errorhandler(404)
def not_found(error):
    return render_template('error404.html') , 404


@app.errorhandler(500)
def not_found(error):
    return render_template('error500.html'), 500


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400
