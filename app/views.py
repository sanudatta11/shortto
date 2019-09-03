import os
import re
import requests
import validators
import random, string
import datetime
try:
    from urllib.parse import unquote
except ImportError:
     from urlparse import unquote
import hashlib
from flask import json, flash
from flask import render_template, flash, redirect, request, session, make_response, current_app, send_from_directory, \
    url_for
from werkzeug.security import safe_str_cmp
from flask_bcrypt import generate_password_hash, check_password_hash

from app import app, db, login_manager
from app.models import Links, User, Announcement, Bundle , ForgotPassword
from config import BCRYPT_LOG_ROUNDS, Auth, blacklist, BASE_URL, SIGNUP_TEMPLATE_ID, SIGNUP_COMPLETE_ID, FORGOT_COMPLETE_ID , PASSWORD_RESET_SUCCESFULL_ID

from flask_login import current_user, login_user, login_required, logout_user
from functools import wraps

import json
from sendgrid import SendGridAPIClient, Email, Content, Substitution
from sendgrid.helpers.mail import Mail

# Google Auth
import functools
from authlib.client import OAuth2Session
import google.oauth2.credentials
import googleapiclient.discovery

ACCESS_TOKEN_URI = 'https://www.googleapis.com/oauth2/v4/token'
AUTHORIZATION_URL = 'https://accounts.google.com/o/oauth2/v2/auth?access_type=offline&prompt=consent'

AUTHORIZATION_SCOPE = 'openid email profile'

AUTH_REDIRECT_URI = os.environ.get("FN_AUTH_REDIRECT_URI") or Auth.REDIRECT_URI
BASE_URI = os.environ.get("FN_BASE_URI") or Auth.BASE_URI
DASH_URI = os.environ.get("FN_DASH_URI") or Auth.DASH_URI
CLIENT_ID = os.environ.get("CLIENT_ID") or Auth.CLIENT_ID
CLIENT_SECRET = os.environ.get("CLIENT_SECRET") or Auth.CLIENT_SECRET

AUTH_TOKEN_KEY = 'auth_token'
AUTH_STATE_KEY = 'auth_state'

random_length = 7
max_url_length = 50


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@login_manager.unauthorized_handler
def unauthorized():
    flash(u'Login Expired! Try Again', 'error')
    return redirect(url_for('login', next=request.endpoint))


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


def redirect_dest(fallback):
    dest = request.args.get('next')
    try:
        dest_url = url_for(dest)
    except:
        return redirect(fallback)
    return redirect(dest_url)


def recaptcha_validate(g_captcha_response, remoteip):
    returnObj = {}
    returnObj['status'] = False
    returnObj['error'] = ''
    data = {'secret': Auth.RECAPTCHA_SECRET, 'response': g_captcha_response, 'remoteip': remoteip}
    post_obj = requests.post("https://www.google.com/recaptcha/api/siteverify", data=data)
    if post_obj.status_code == 200:
        json_data = json.loads(post_obj.text)
        if json_data['success'] == True:
            returnObj['status'] = True
        else:
            returnObj['error'] = str(json_data['error-codes'][0])
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

def changetomd5(long_url, count=0):
    if count != 0:
        long_url = long_url + str(count)
    data = hashlib.md5(long_url.encode())
    data = data.hexdigest()
    md5result = (data[:random_length]) if len(data) > random_length else data
    return str(md5result)


# End of Short URL Def

@app.route('/', methods=['GET'])
def index():
    tot_users = User.query.count()
    tot_urls = Links.query.count()
    tot_clicks_obj = db.session.query(Links, db.func.sum(Links.clicks))
    tot_clicks = tot_clicks_obj[0][1]
    return render_template('index.html', tot_clicks=tot_clicks, tot_urls=tot_urls,tot_users=tot_users)


@app.route('/dashboard', methods=['GET'])
@app.route('/dashboard/', methods=['GET'])
@login_required
def dashboard():
    announcement_to_publish = Announcement.query.filter(Announcement.end_date > datetime.datetime.utcnow()).order_by(
        Announcement.id.desc()).first()
    sort_method = request.args.get('sort')
    top_urls = user_links = Links.query.filter(Links.user==current_user,Links.archieved==False).order_by(Links.clicks.desc()).all()
    bundles = Bundle.query.filter(Links.user==current_user,Links.archieved==False).all()
    if sort_method == "newest":
        user_links = Links.query.filter(Links.user==current_user,Links.archieved==False).order_by(Links.created_at.desc()).all()
    elif sort_method == "popular":
        user_links = top_urls
    elif sort_method == "expired":
        user_links = Links.query.filter(Links.user==current_user,Links.expiration_date <= datetime.datetime.utcnow()).order_by(Links.created_at.desc()).all()
    elif sort_method == "archieve":
        user_links = Links.query.filter(Links.user==current_user,Links.archieved==True).all()
    else:
        user_links = Links.query.filter(Links.user==current_user,Links.archieved==False).all()
    return render_template('dashboard.html', announcement=announcement_to_publish, user_links=user_links,
                           current_date=datetime.datetime.now(), top_urls=top_urls,base_url=BASE_URL,bundles=bundles)


@app.route('/dashboard/shorten', methods=['POST'])
@app.route('/dashboard/shorten/', methods=['POST'])
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
            flash(temp.show_url(), 'url-done')
            return redirect(url_for('dashboard'))
        return redirect(url_for('dashboard'))
    except:
        flash(u'Something Went Wrong! Please try again!', 'error')
        return redirect(url_for('login'))

@app.route('/link/edit/<short_url>', methods=['GET','POST'])
@login_required_save_post
def link_edit(short_url):
    link = Links.query.filter(Links.short_url == short_url, Links.user == current_user).first()
    if link:
        if request.method == 'GET':
            return render_template('edit_link.html',link=link)
        else:
            new_password = request.form['password']
            link.password_protect = True
            link.password_hash = generate_password_hash(new_password, BCRYPT_LOG_ROUNDS)
            db.session.commit()
            flash(u'Password has been successfully updated for the Link!', 'success')
        return redirect(url_for('link_edit', short_url=short_url))
    else:
        flash(u'Link is invalid or not present', 'error')
        return redirect(url_for('dashboard'))

@app.route('/link/delete/', methods=['POST'])
@login_required_save_post
def link_delete():
    short_url = request.form['short_url']
    print(short_url)
    link = Links.query.filter(Links.short_url == short_url, Links.user == current_user).first()
    if link:
        db.session.delete(link)
        db.session.commit()
        flash(u'Link has been deleted successfully', 'success')
    else:
        flash(u'Some Error Occured! Try again later', 'error')
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@app.route('/profile/', methods=['GET', 'POST'])
@login_required_save_post
def profile():
    if request.method == "POST":
        password = request.form['password']
        cpassword = request.form['cpassword']
        if current_user.google_login:
            flash(u"Google SignIn Users cannot change password!", "error")
        elif not password or not cpassword:
            flash(u"Password not Provided!", "error")
        elif password != cpassword:
            flash(u"Passwords donot match!", "error")
        elif len(password) < 5:
            flash(u"Password length less than 5 characters!", "warning")
        else:
            passh = generate_password_hash(password, BCRYPT_LOG_ROUNDS)
            current_user.password_hash = passh
            db.session.commit()
            flash(u'Password updated successfully!', 'success')
        return redirect(url_for("profile"))
    else:
        return render_template('profile.html')


@app.route('/bundles', methods=['GET'])
@app.route('/bundles/', methods=['GET'])
@login_required_save_post
def bundle():
    bundle_data = Bundle.query.filter_by(user=current_user).all()
    if request.args.get('bundle'):
        bundle_id = request.args.get('bundle')
        bundle = Bundle.query.filter(Bundle.user == current_user, Bundle.id == bundle_id).first()
        if len(bundle.links):
            return render_template('bundle.html', bundles=bundle_data, link_bundle=bundle,
                                   current_date=datetime.datetime.now())
        else:
            return render_template('bundle.html', bundles=bundle_data, blank_link=True,
                                   current_date=datetime.datetime.now())
    return render_template('bundle.html', bundles=bundle_data, current_date=datetime.datetime.now())


@app.route('/bundle/add/url', methods=['POST'])
@app.route('/bundle/add/url/', methods=['POST'])
@login_required_save_post
def bundle_add_url():
    short_url = request.form.get('short_url')
    bundle_id = request.form.get('bundle_id')
    # print(short_url,bundle_id)
    bundle = Bundle.query.filter_by(id=bundle_id,user=current_user).first()
    link = Links.query.filter(Links.user==current_user,Links.short_url==short_url).first()
    if bundle and link:
        link.bundle = bundle
        db.session.commit()
        flash(u'Link has been added to the bundle', 'success')
    else:
        flash(u'Bundle and Link Mismatch to Account!','error')
    return redirect(url_for('dashboard'))

@app.route('/archieve/<short_url>',methods=['GET'])
@login_required_save_post
def archieve_url(short_url):
    if short_url:
        short_url_obj = Links.query.filter_by(short_url=short_url,user=current_user).first()
        if short_url_obj:
            if not short_url_obj.archieved:
                short_url_obj.archieved = True
                db.session.commit()
                flash(u'Short URL Has been Archieved!','success')
            else:
                short_url_obj.archieved = False
                db.session.commit()
                flash(u'Short URL Has been UnArchieved!', 'success')
        else:
            flash(u'Short URL not found!','error')
    else:
        flash(u'Short URL find error!', 'error')
    return redirect(url_for('dashboard'))

@app.route('/bundle/add', methods=['POST'])
@app.route('/bundle/add/', methods=['POST'])
@login_required_save_post
def bundle_add():
    bundle_name = request.form['bundle_name']
    if bundle_name and re.match("^[a-zA-Z\d\-_\s]+$", bundle_name):
        bundle = Bundle(name=bundle_name, user=current_user)
        db.session.add(bundle)
        db.session.commit()
        flash(u'Bundle added successfully', 'success')
    else:
        flash(u'Bundle Name contains Invalid Characters', 'error')
        flash(u'Only Allowed characters (a-zA-Z-_)', 'error')
    return redirect(url_for('bundle'))


@app.route('/bundle/edit', methods=['POST'])
@app.route('/bundle/edit/', methods=['POST'])
@login_required_save_post
def bundle_edit():
    new_bundle_name = request.form['new_bundle_name']
    bundle_id = request.form['bundle_id']
    if new_bundle_name and re.match("^[a-zA-Z\d\-_\s]+$", new_bundle_name):
        bundle = Bundle.query.filter(Bundle.user == current_user, Bundle.id == bundle_id).first()
        bundle.name = new_bundle_name
        db.session.commit()
        flash(u'Bundle updated successfully', 'success')
    else:
        flash(u'Bundle Name contains Invalid Characters', 'error')
        flash(u'Only Allowed characters (a-zA-Z-_)', 'error')
    return redirect(url_for('bundle'))


@app.route('/bundle/delete', methods=['POST'])
@app.route('/bundle/delete/', methods=['POST'])
@login_required_save_post
def bundle_delete():
    try:
        bundle_id = request.form['bundle_id']
        bundle = Bundle.query.filter(Bundle.user == current_user, Bundle.id == bundle_id).first()
        if bundle:
            if(len(bundle.links)):
                flash(u'Please delete all URLs in the bundle before deleting it!','error')
            else:
                db.session.delete(bundle)
                db.session.commit()
                flash(u'Bundle deleted successfully', 'success')
        else:
            flash(u'Bundle find Error', 'warning')
    except Exception as e:
        print(e)
        flash(u'Some Error Occurred! Try Again', 'error')
    finally:
        return redirect(url_for('bundle'))


@app.route('/self/terms', methods=['GET'])
@app.route('/self/terms/', methods=['GET'])
def terms():
    return render_template('terms.html')


@app.route('/self/policy', methods=['GET'])
@app.route('/self/policy/', methods=['GET'])
def policy():
    return render_template('gdpr.html')


@app.route('/login', methods=['GET', 'POST'])
@app.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect_dest(fallback=url_for('dashboard'))
    elif request.method == "POST":
        g_captcha_response = request.form['g-captcha-client-key']
        resp = recaptcha_validate(g_captcha_response, request.remote_addr)
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if not resp['status']:
            flash(u'Recaptcha Validation Error', 'error')
            return redirect(url_for('login'))
        elif user:
            # User Present
            if (user.google_login):
                flash(u'Your account is signed up via Google! Please use Google Sign In', 'error')
                return redirect(url_for('login'))
            elif (not user.confirmed):
                flash(u'Please confirm your email by clicking on the link sent to you', 'error')
                return redirect_dest(fallback=url_for('dashboard'))
            elif (check_password_hash(user.password_hash, password)):
                # All cool
                flash(u'You have been successfully logged in.', 'success')
                login_user(user)
                return redirect_dest(fallback=url_for('dashboard'))
            else:
                flash(u'Email or Password Incorrect!', 'error')
                return redirect(url_for('login'))
        else:
            flash(u'Email or Password Incorrect!', 'error')
            return redirect(url_for('login'))
    return render_template('login.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop(AUTH_TOKEN_KEY, None)
    session.pop(AUTH_STATE_KEY, None)
    return redirect(url_for('index'))


# noinspection PyArgumentList
@app.route('/register', methods=['GET', 'POST'])
@app.route('/register/', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        username = request.form['username']
        email = request.form['email']
        passw = request.form['password']
        cpassw = request.form['cpassword']

        error = []
        if not firstName:
            error = True
            flash(u"First Name not Provided!", "error")
        if not lastName:
            error = True
            flash(u"Last Name not Provided!", "error")
        if not username:
            error = True
            flash(u"Username not Provided!", "error")
        if not email:
            error = True
            flash(u"Email not Provided!", "error")
        if not passw or not cpassw:
            error = True
            flash(u"Password not Provided!", "error")
        if passw != cpassw:
            error = True
            flash(u"Passwords donot match!", "error")
        if len(passw) < 5:
            error = True
            flash(u"Password length less than 5!", "warning")
        if User.query.filter_by(username=username).count() > 0:
            error = True
            flash(u"Username is taken!", "warning")
        if User.query.filter_by(email=email).count() > 0:
            error = True
            flash(u"Email is already registered!", "error")
        if error:
            return redirect(url_for("register"))
        passh = generate_password_hash(passw, BCRYPT_LOG_ROUNDS)
        confirmationHash = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        try:
            sendgrid_client = SendGridAPIClient(os.environ.get('MAIL_SENDGRID_API_KEY'))
            from_email = 'support@shortto.com'
            mail = Mail(from_email=from_email, subject='Welcome to Short To!', to_emails=email)
            URI = BASE_URL + 'email/verification/' + str(confirmationHash) + '/' + str(email)
            mail.dynamic_template_data = {
                'firstName' : firstName,
                'redirect_url' : URI
            }
            mail.template_id = SIGNUP_TEMPLATE_ID
            response = sendgrid_client.send(mail)
            # print(response.status_code)
            # print(response.body)
            # print(response.headers)
        except Exception as e:
            print(e)
            flash(u'Email Confirmation Error!','error')
            return redirect(url_for('login'))

        register = User(firstName=firstName, lastName=lastName, email=email, password_hash=passh, username=username,confirmationHash=confirmationHash)
        db.session.add(register)
        db.session.commit()
        flash(u'You were successfully registered! Please verify your email. Check your Spam Folders too!', 'success')
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route('/email/verification/<string:confirmationHash>/<string:email>',methods=['GET'])
@app.route('/email/verification/<string:confirmationHash>/<string:email>/',methods=['GET'])
def email(confirmationHash,email):
    try:
        email = unquote(email)
        confirmationHash = unquote(confirmationHash)
        user = User.query.filter_by(email=email, confirmed=False, confirmationHash=confirmationHash).first()
        if user:
            user.confirmed = True
            user.confirmationHash = None
            db.session.commit()
            flash(u'Your email has been verified!', 'success')
            return redirect(url_for('emailDone'))
        else:
            print("Not done")
            flash(u'Code Invalid or expired', 'error')
            return redirect(url_for('emailDone'))
    except Exception as e:
        print(e)
        flash(u'Some Error Occured!', 'error')
        return redirect(url_for('emailDone'))

@app.route('/email/done',methods=['GET'])
@app.route('/email/done/',methods=['GET'])
def emailDone():
    return render_template('emailDone.html')

# End of Test Routes for new UI


# Google Auth Based Routes
@app.route('/google/login')
@no_cache
def loginGoogle():
    sessionObj = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                               scope=AUTHORIZATION_SCOPE,
                               redirect_uri=AUTH_REDIRECT_URI)

    uri, state = sessionObj.create_authorization_url(AUTHORIZATION_URL)
    session[AUTH_STATE_KEY] = state
    session.permanent = True
    return redirect(uri, code=302)


# noinspection PyArgumentList
@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    req_state = request.args.get('state', default=None, type=None)
    print("Request State=",req_state)
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
    if (not user):
        firstName = user_info['given_name']
        lastName = user_info['family_name']
        email = user_info['email']
        picture = user_info['picture']
        locale = user_info['locale']
        newUser = User(firstName=firstName, lastName=lastName, email=email, picture=picture, google_login=True,locale=locale,confirmed=True)
        db.session.add(newUser)
        db.session.commit()
        login_user(newUser)
        try:
            sendgrid_client = SendGridAPIClient(os.environ.get('MAIL_SENDGRID_API_KEY'))
            from_email = 'support@shortto.com'
            mail = Mail(from_email=from_email, subject='Welcome to ShortTo!', to_emails=email)
            mail.dynamic_template_data = {
                'firstName' : firstName
            }
            mail.template_id = SIGNUP_COMPLETE_ID
            response = sendgrid_client.send(mail)
            # print(response.status_code)
            # print(response.body)
            # print(response.headers)
        except Exception as e:
            print(e)
            flash(u'Email Confirmation Error!','error')
            return redirect(url_for('dashboard'))
    elif(user.google_login == False):
        flash(u'Your account is created via Password! Please login via Password!.', 'error')
        return redirect(url_for('login'))
    else:
        login_user(user)
    flash(u'You have been successfully logged in.', 'success')
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

@app.route('/debug-sentry')
def trigger_error():
    division_by_zero = 1 / 0


@app.route('/forgotPassword',methods=['POST'])
@app.route('/forgotPassword/',methods=['POST'])
def forgotPassword():
    g_captcha_response = request.form['g-captcha-client-key-2']
    resp = recaptcha_validate(g_captcha_response, request.remote_addr)
    email = request.form['email']
    if not resp['status']:
        print(resp)
        flash(u'Recaptcha Validation Error', 'error')
    elif not(email and validators.email(email)):
        flash(u'Email Invalid!','error')
    else:
        resetHash = ''.join(random.choices(string.ascii_letters + string.digits, k=50))
        user = User.query.filter_by(email=email).first()
        if user:
            if user.google_login == True:
                flash(u'Your account is created via Google Login! Password reset not possible.','error')
                return redirect(url_for('login'))
            newForgot = ForgotPassword(resetHash=resetHash)
            newForgot.user = user
            try:
                sendgrid_client = SendGridAPIClient(os.environ.get('MAIL_SENDGRID_API_KEY'))
                from_email = 'support@shortto.com'
                mail = Mail(from_email=from_email,to_emails=email)
                URI = BASE_URL + 'user/forgot/' + str(resetHash) + '/' + str(email) + '/'
                mail.dynamic_template_data = {
                    'firstName' : user.firstName,
                    'resetLink' : URI
                }
                mail.template_id = FORGOT_COMPLETE_ID
                response = sendgrid_client.send(mail)
                db.session.add(newForgot)
                db.session.commit()
                # print(response.status_code)
                # print(response.body)
                # print(response.headers)
            except Exception as e:
                print(e)
                flash(u'Forgot Email Error!','error')
                return redirect(url_for('login'))
        flash(u'If an active account is associated with this email, you should receive a reset email shortly.','success')
    return redirect(url_for('login'))

@app.route('/user/forgot/<reset_hash>/<email>',methods=['GET','POST'])
@app.route('/user/forgot/<reset_hash>/<email>/',methods=['GET','POST'])
def forgotPasswordConfirm(reset_hash,email):
    reset_hash = unquote(reset_hash)
    email = unquote(email)
    newForgot = ForgotPassword.query.filter_by(resetHash=reset_hash).first()
    if newForgot and newForgot.user.email == email:
        if request.method == 'GET':
            return render_template('forgotPassword.html')
        else:
            password = request.form['password']
            cpassword = request.form['cpassword']
            if password != cpassword:
                flash(u'Password Donot Match','warning')
                return redirect(request.url)
            else:
                user = newForgot.user
                if check_password_hash(user.password_hash,password):
                    flash(u'Your current password matches with your old! Please provide a different Password.','error')
                    return redirect(request.url)
                user.password_hash = generate_password_hash(password,BCRYPT_LOG_ROUNDS)
                db.session.delete(newForgot)
                try:
                    sendgrid_client = SendGridAPIClient(os.environ.get('MAIL_SENDGRID_API_KEY'))
                    from_email = 'support@shortto.com'
                    mail = Mail(from_email=from_email, to_emails=email,subject="Password Reset Successful")
                    mail.dynamic_template_data = {
                        'firstName': user.firstName
                    }
                    mail.template_id = PASSWORD_RESET_SUCCESFULL_ID
                    response = sendgrid_client.send(mail)
                    db.session.commit()
                    flash(u'Password Reset Successful', 'success')
                except Exception as e:
                    print(e)
                    flash(u'Forgot Email Error!', 'error')
                return redirect(url_for('login'))
    else:
        flash(u'Invalid Link! Please reset your password again','error')
        return redirect(url_for('login'))


# Warning CRTICAL ROUTE
@app.route('/<string:short_url>', methods=['GET','POST'])
@app.route('/<string:short_url>/', methods=['GET','POST'])
def routeit(short_url):
    if request.method == "GET":
        link = Links.query.filter_by(short_url=short_url).first()
        if link:
            if link.password_protect:
                return render_template('password_url.html')
            else:
                link.clicks += 1
                db.session.commit()
                url = link.big_url
                if not validators.url(url):
                    return render_template('index.html', url_error=True)
                return redirect(url, code=302)
    elif request.method == "POST":
        password = request.form['password']
        if password:
            link = Links.query.filter_by(short_url=short_url).first()
            if link and check_password_hash(link.password_hash,password):
                return redirect(link.big_url,code=302)
            else:
                flash(u'Link or Password incorrect!','error')
                return redirect(url_for('routeit',short_url=short_url))
        flash(u'Password not appropriate!', 'error')
        return redirect(url_for('routeit', short_url=short_url))
    return render_template('notfound.html')


# END OF CRITICAL ROUTE

@app.errorhandler(404)
def not_found(error):
    return render_template('error404.html'), 404


@app.errorhandler(500)
def not_found(error):
    return render_template('error500.html'), 500