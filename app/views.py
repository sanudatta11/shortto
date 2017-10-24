from flask import render_template,flash, redirect,request
from app import app, db
from app.models import Shortto, User
from app.forms import Url_form, Login


@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
def index():
    form = Url_form(request.form)
    if request.method == 'POST' and form.validate():
        if request.form['to_url']:
            #Check if unique or not
            if Shortto.query.filter_by(short_url=request.form['to_url']).count() > 0:
                #Already Used Short Url
                return "There"
            #Url Not Present
            temp = Shortto(big_url=request.form['from_url'],short_url=request.form['to_url'])
            db.session.add(temp)
            db.session.commit()
            return "Done"

    return render_template('index.html',form=form)

@app.route('/<string:short_data>',methods=['GET'])
def routeit(short_data):
    temp = Shortto.query.filter_by(short_url=short_data).first()
    if temp is not None:
        url = temp.big_url
        return redirect(url,code=302)
    return "Url Not There"

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        form_temp = Login(request.form)
        if form_temp.validate():
            email = request.form['email']
            password = request.form['password']
            user = User.query.filter_by(email=request.form['email']).first()
            if user and user.check_pass(password):
                flash('Logged In')
                return redirect('/success/',code=302)
            else:
                flash('Wrong Credentials')
                return render_template('failed.html',code=500)
        else:
            flash('Not Valid Data')
            form = Login()
            return render_template('login.html',form=form)
    elif request.method == 'GET':
        form = Login()
        return render_template('login.html',form=form)
