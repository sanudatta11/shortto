import os
import re
import requests
import validators
import random
import datetime
import hashlib
from flask import json,flash
from flask import render_template, flash, redirect, request,session, make_response, current_app, send_from_directory, url_for
from werkzeug.security import safe_str_cmp
from flask_bcrypt import generate_password_hash,check_password_hash

from app import app, db,login_manager
from app.models import Links, User, Announcement, Bundle
from config import BCRYPT_LOG_ROUNDS,Auth,blacklist

from flask_login import current_user, login_user, login_required, logout_user
from functools import wraps
from werkzeug.datastructures import MultiDict

# Google Auth
import functools
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery


ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE ='openid email profile'

AUTH_REDIRECT_URI = os.environ.get("FN_AUTH_REDIRECT_URI", default=False) or Auth.REDIRECT_URI
BASE_URI = os.environ.get("FN_BASE_URI", default=False) or Auth.BASE_URI
DASH_URI = os.environ.get("FN_DASH_URI", default=False) or Auth.DASH_URI
CLIENT_ID = os.environ.get("FN_CLIENT_ID", default=False) or Auth.CLIENT_ID
CLIENT_SECRET = os.environ.get("FN_CLIENT_SECRET", default=False) or Auth.CLIENT_SECRET

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

random_length = 7
max_url_length = 50

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@login_manager.unauthorized_handler
def unauthorized():
    flash(u'Login Expired! Try Again','error')
    return redirect(url_for('login'))

def login_required_save_post(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if current_app.login_manager._login_disabled or current_user.is_authenticated:
            # auth disabled or already logged in
            return f(*args, **kwargs)

        # store data before handling login
        session['form_data'] = request.form.to_dict(flat=False)
        session['form_path'] = request.path
        return current_app.login_manager.unauthorized()

    return decorated

def recaptcha_validate(g_captcha_response,remoteip):
    returnObj = {}
    returnObj['status'] = False
    returnObj['error'] = ''
    data = {'secret':  Auth.RECAPTCHA_SECRET,'response': g_captcha_response,'remoteip': remoteip}
    post_obj = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
    if post_obj.status_code == 200:
        json_data = json.loads(post_obj.text)
        if json_data['success'] == True:
            returnObj['status'] = True
        else:
            returnObj['error']=str(json_data['error-codes'][0])
    return returnObj

# Google Auth Def


def is_logged_in():
    return True if AUTH_TOKEN_KEY in session else False

def build_credentials():
    if not is_logged_in():
        raise Exception('User must be logged in')

    oauth2_tokens = session[AUTH_TOKEN_KEY]
    
    return google.oauth2.credentials.Credentials(
                oauth2_tokens['access_token'],
                refresh_token=oauth2_tokens['refresh_token'],
                client_id=CLIENT_ID,
                client_secret=CLIENT_SECRET,
                token_uri=ACCESS_TOKEN_URI)

def get_user_info():
    credentials = build_credentials()
    oauth2_client = googleapiclient.discovery.build(
                        'oauth2', 'v2',
                        credentials=credentials)

    return oauth2_client.userinfo().get().execute()

def no_cache(view):
    @functools.wraps(view)
    def no_cache_impl(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '-1'
        return response

    return functools.update_wrapper(no_cache_impl, view)

# End of Google Auth Def

# Short URL Def

def changetomd5(long_url,count=0):
    if count!=0:
        long_url = long_url + str(count)
    data = hashlib.md5(long_url.encode())
    data = data.hexdigest()
    md5result = (data[:random_length]) if len(data) > random_length else data
    return str(md5result)

# End of Short URL Def

@app.route('/', methods=['GET', 'POST'])
def index():
    tot_urls = Links.query.count()
    tot_clicks_obj = db.session.query(Links, db.func.sum(Links.clicks))
    tot_clicks = tot_clicks_obj[0][1]
    return render_template('index.html', tot_clicks=tot_clicks, tot_urls=tot_urls)

@app.route('/dashboard', methods=['GET'])
@app.route('/dashboard/', methods=['GET'])
@login_required
def dashboard():
    announcement_to_publish = Announcement.query.filter(Announcement.end_date>datetime.datetime.utcnow()).order_by(Announcement.id.desc()).first()
    user_links = Links.query.filter_by(user=current_user).all()
    return render_template('dashboard.html',announcement=announcement_to_publish,user_links=user_links,current_date = datetime.datetime.now())

@app.route('/dashboard/shorten',methods=['POST'])
@app.route('/dashboard/shorten/',methods=['POST'])
@login_required_save_post
def dashboardShorten():
    try:
        if request.method == 'POST':
            print(current_user.is_authenticated)
            if not current_user.is_authenticated:
                flash(u'Login Expired! Try Again', 'error')
                return redirect(url_for('login'))
            long_url = request.form['long_url']
            short_url = request.form['short_url']
            expiration_date = request.form['expiration_date']
            description = request.form['description']
            password = request.form['password']

            if not long_url:
                flash(u'Long URL not provided', 'error')
                return redirect(url_for('dashboard'))

            g_captcha_response = request.form['g-captcha-client-key']
            resp = recaptcha_validate(g_captcha_response, request.remote_addr)
            if not resp['status']:
                print(resp)
                flash(u'Recaptcha Validation Error', 'error')
                return redirect(url_for('login'))
            # Recaptcha End

            for url_s in blacklist:
                url_s_1 = '://' + url_s
                url_s_2 = 'www.' + url_s
                if (url_s_1 in long_url.lower()) or (url_s_2 in long_url.lower()):
                    flash(u'URL Provided is Blacklisted', 'error')
                    return redirect(url_for('dashboard'))

            if not validators.url(long_url):
                flash(u'URL Provided is Invalid', 'error')
                return redirect(url_for('dashboard'))

            if short_url:
                if not re.match("^[a-zA-Z]{4}[A-Za-z0-9-]+$", short_url):
                    flash(
                        u'URL Provided doesn\'t pass validation! Must be between 5 to 16 Characters. Only Allowed(a-z-A-Z and Hyphen)',
                        'error')
                    return redirect(url_for('dashboard'))
                # Check if unique or not
                elif Links.query.filter_by(short_url=short_url).count() > 0:
                    # Already Used Short URL
                    flash(u'Short URL is already Used', 'warning')
                    return redirect(url_for('dashboard'))
            else:
                # Short URL Not Provided
                tries = 150
                countMd5 = 7000
                while tries > 0:
                    tries = tries - 1
                    numToSend = random.randrange(countMd5)
                    short_url = changetomd5(long_url, numToSend)
                    if (Links.query.filter_by(short_url=short_url).count() > 0):
                        countMd5 = countMd5 + 10
                    else:
                        break
            temp = Links(big_url=long_url, short_url=short_url)
            temp.user = current_user
            if password:
                temp.password_protect = True
                temp.password_hash = generate_password_hash(password, BCRYPT_LOG_ROUNDS)
            if description:
                temp.description = description
            if expiration_date:
                temp.expiration = True
                expiration_date = datetime.datetime.strptime(expiration_date, '%m/%d/%Y').date()
                temp.expiration_date = expiration_date
            db.session.add(temp)
            db.session.commit()
            flash(u'URL created Successfully', 'success')
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    except:
        flash(u'Something Went Wrong! Please try again!', 'error')
        return redirect(url_for('login'))

@app.route('/profile',methods=['GET'])
@app.route('/profile/',methods=['GET'])
def profile():
    return render_template('profile.html')

@app.route('/self/terms', methods=['GET'])
@app.route('/self/terms/', methods=['GET'])
def terms():
    return render_template('terms.html')

@app.route('/self/policy', methods=['GET'])
@app.route('/self/policy/', methods=['GET'])
def policy():
    return render_template('gdpr.html')

@app.route('/login', methods=['GET','POST'])
@app.route('/login/', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
      return redirect(url_for('dashboard'))
    elif request.method == "POST":
        g_captcha_response = request.form['g-captcha-client-key']
        resp = recaptcha_validate(g_captcha_response,request.remote_addr)
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not resp['status']:
            flash(u'Recaptcha Validation Error','error')
            return redirect(url_for('login'))
        elif user:
            #User Present
            if(user.google_login):
                flash(u'Your account is signed up via Google! Please use Google Sign In','error')
                return redirect(url_for('login'))
            elif(check_password_hash(user.password_hash,password)):
                #All cool
                flash(u'You have been successfully logged in.','success')
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash(u'Email or Password Incorrect!','error')
                return redirect(url_for('login'))
        else:
            flash(u'Email or Password Incorrect!','error')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET','POST'])
@app.route('/register/', methods=['GET','POST'])
def register():
    if request.method == "POST":
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        passw = request.form['password']
        cpassw = request.form['cpassword']
        
        error = []
        if(not firstName):
            error = True
            flash(u"First Name not Provided!","error")
        if(not lastName):
            error = True
            flash(u"Last Name not Provided!","error")
        if(not email):
            error = True
            flash(u"Email not Provided!","error")
        if(not passw or not cpassw):
            error = True
            flash(u"Password not Provided!","error")
        if(passw != cpassw):
            error = True
            flash(u"Passwords donot match!","error")
        if(error):
            return redirect(url_for("register"))
        
        passh = generate_password_hash(passw, BCRYPT_LOG_ROUNDS)
        register = User(firstName = firstName,lastName = lastName, email = email, password_hash = passh)
        db.session.add(register)
        db.session.commit()
        flash(u'You were successfully registered', 'success')
        return redirect(url_for("login"))
    return render_template("register.html")

# End of Test Routes for new UI

#Warning CRTICAL ROUTE 
@app.route('/<string:short_data>', methods=['GET'])
@app.route('/<string:short_data>/', methods=['GET'])
def routeit(short_data):
    temp = Links.query.filter_by(short_url=short_data).first()
    if temp is not None:
        temp.clicks += 1
        db.session.commit()
        url = temp.big_url
        if not validators.url(url):
            return render_template('index.html',url_error=True)
        return redirect(url, code=302)
    return render_template('notfound.html')


#END OF CRITICAL ROUTE

# Google Auth Based Routes
@app.route('/google/login')
@no_cache
def loginGoogle():
    sessionObj = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)
  
    uri, state = sessionObj.authorization_url(AUTHORIZATION_URL)
    session[AUTH_STATE_KEY] = state
    session.permanent = True
    return redirect(uri, code=302)

@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    req_state = request.args.get('state', default=None, type=None)

    if req_state != session[AUTH_STATE_KEY]:
        response = make_response('Invalid state parameter', 401)
        return response
    
    sessionObj = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            state=session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_REDIRECT_URI)

    oauth2_tokens = sessionObj.fetch_access_token(
                        ACCESS_TOKEN_URI,            
                        authorization_response=request.url)
    session[AUTH_TOKEN_KEY] = oauth2_tokens
    user_info = get_user_info()
    user = User.query.filter_by(email=user_info['email']).first()
    if(not user):
        firstName = user_info['given_name']
        lastName = user_info['family_name']
        email = user_info['email']
        picture = user_info['picture']
        locale = user_info['locale']
        newUser = User(firstName=firstName, lastName=lastName, email=email,picture=picture,google_login=True,locale=locale)
        db.session.add(newUser)
        db.session.commit()
        login_user(newUser)
    else:
        login_user(user)
    flash(u'You have been successfully logged in.','success')
    return redirect(url_for('dashboard'))

@app.route('/google/logout')
@no_cache
def googleLogout():
    session.pop(AUTH_TOKEN_KEY, None)
    session.pop(AUTH_STATE_KEY, None)

    return redirect(BASE_URI, code=302)


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
