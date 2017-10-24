from flask import render_template,flash, redirect,request
from app import app, db
from app.models import shortto
from app.forms import Url_form


@app.route('/',methods=['GET','POST'])
@app.route('/index',methods=['GET','POST'])
def index():
    form = Url_form(request.form)
    if request.method == 'POST' and form.validate():
        if request.form['to_url']:
            #Check if unique or not
            if shortto.query.filter_by(short_url=request.form['to_url']).count() > 0:
                #Already Used Short Url
                return "There"
            #Url Not Present
            temp = shortto(big_url=request.form['from_url'],short_url=request.form['to_url'])
            db.session.add(temp)
            db.session.commit()
            return "Done"

    return render_template('index.html',form=form)
