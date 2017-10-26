from flask import render_template, flash, redirect, request,session
from app import app, db
from app.models import Shortto, User
from sqlalchemy import func
from app.forms import Url_form, Login
from app.helper import idtoshort_url
from flask_wtf.csrf import CSRFError

@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = Url_form(request.form)
    if request.method == 'POST' and request.form['from_url']:
        if request.form['to_url']:
            # Check if unique or not
            if Shortto.query.filter_by(short_url=request.form['to_url']).count() > 0:
                # Already Used Short Url
                error_url = True
                return render_template('index.html', code=320, error_url=error_url)
            # Url Not Present
            temp = Shortto(big_url=request.form['from_url'], short_url=request.form['to_url'])
            db.session.add(temp)
            db.session.commit()
            short_url = request.form['to_url']
            return render_template('done.html', code=200, short_url=app.config['BASE_URL'] + short_url)
        else:
            rows = Shortto.query.count()
            rows = int(rows)
            short_url = idtoshort_url(rows+1)
            i = 2
            while Shortto.query.filter_by(short_url=short_url).count() > 0:
                short_url = idtoshort_url(rows + i)
                i = i + 1

            temp = Shortto(big_url=request.form['from_url'], short_url=short_url)
            db.session.add(temp)
            db.session.commit()
            return render_template('done.html',code=200,short_url=app.config['BASE_URL'] + short_url)
    return render_template('index.html', form=form)


@app.route('/<string:short_data>', methods=['GET'])
def routeit(short_data):
    temp = Shortto.query.filter_by(short_url=short_data).first()
    if temp is not None:
        url = temp.big_url
        return redirect(url, code=302)
    return render_template('notfound.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        form_temp = Login(request.form)
        if form_temp.validate():
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=request.form['email']).first()
            if user and user.check_pass(password):
                flash('Logged In')
                return redirect('/success/', code=302)
            else:
                flash('Wrong Credentials')
                return render_template('failed.html', code=500)
        else:
            flash('Not Valid Data')
            form = Login()
            return render_template('login.html', form=form)
    elif request.method == 'GET':
        form = Login()
        return render_template('login.html', form=form)


@app.route('/success')
@app.route('/success/')
def success():
    return "Succeded Auth"


@app.errorhandler(404)
def not_found(error):
    return render_template('error404.html') , 404


@app.errorhandler(CSRFError)
def handle_csrf_error(e):
    return render_template('csrf_error.html', reason=e.description), 400
