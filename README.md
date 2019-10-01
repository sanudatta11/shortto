# Welcome to ShortTo!

Using Flask to build a URL Shortening Service ShortTo

Integration with  Flask-Cors, Flask-Testing, Flask-SQLalchemy,and Flask-OAuth and other extensions

### Extension:

- SQL ORM: [Flask-SQLalchemy](http://flask-sqlalchemy.pocoo.org/2.1/)

- Testing: [Flask-Testing](http://flask.pocoo.org/docs/0.12/testing/)

- OAuth: [Flask-OAuth](https://pythonhosted.org/Flask-OAuth/)

- ESDAO: [elasticsearch](https://elasticsearch-py.readthedocs.io/en/master/) , [elasticsearch-dsl](http://elasticsearch-dsl.readthedocs.io/en/latest/index.html)


## Installation

There are two requirements file. The file named `requirements-prod` should be used only on production deployments and can work only on UNIX based operating systems.

Install with pip:

```
$ pip install -r requirements.txt
```

## Application Structure 
```
.
| |────app/
| | |────views.py
| | |────models.py
| | |────__init__.py
| | |────static/
| | |──────js/
| | |──────css/
| | |──────img/
| |────tempaltes/

```


## Flask Configuration

#### Example

```
app = Flask(__name__)
app.config['DEBUG'] = True //Only use it in Development
```
### Configuring From Files

#### Example Usage

```
app = Flask(__name__ )
app.config.from_pyfile('config.Development.cfg')
```

#### cfg example

```

##Flask settings
DEBUG = True  # True/False
TESTING = False

##SWAGGER settings
SWAGGER_DOC_URL = '/api'

....


```

## Configuring Local Database

### Run the following for starting DB initialization 
In flask we use Alchemy as our default DDL. 

`flask db init` 
`flask db migrate -m "<YOUR MESSAGE>"`
`flask db upgrade`


 
## Run Flask
### Run flask for develop
```
$ python application.py
```
In flask, Default port is `8000`

Your application will be live in `http://127.0.0.1:8000/`

Swagger document page:  `http://127.0.0.1:5000/api`

### Run flask for production

** Run with gunicorn **

In  webapp/

```
$ gunicorn -w 4 -b 127.0.0.1:5000 run:app

```

* -w : number of worker
* -b : Socket to bind


### Run with Docker

```
$ docker build -t shortto .

$ docker run -p 80:8000 --name shortto shortto
 
```

## Deploy to Production Build

### Build the Docker Image for Production Deployments
```
$ docker build -t shortto .
$ docker tag shortto <username>/<tag>
$ docker login
$ docker push <username>/<tag>
```

### Input Environment Variables while Running

1. CLIENT_ID - Google Sign In API Client ID
2. CLIENT_SECRET  - Google Sign In API Secret
3. ENVIRONMENT - PRODUCTION
4. MAIL_SENDGRID_API_KEY - API Key for Sendgrid
5. MEMCACHED_URL - Memcached URI for Session Caching (Not in USE)
6. RDS_DBNAME - DB Name for RDS
7. RDS_HOST - Host Name for the RDS
8. RDS_PASS
9. RDS_PORT
10. RDS_USER - DB User name for RDS
11.  RECAPTCHA_SECRET - Google Re captcha Secret Key
12. SAFE_BROWSING_KEY - Google Safe Browsing Key


## Unittest
```
$ nosetests webapp/ --with-cov --cover-html --cover-package=app
```
- --with-cov : test with coverage
- --cover-html: coverage report in html format

## Reference

Offical Website

- [Flask](http://flask.pocoo.org/)
- [Flask Extension](http://flask.pocoo.org/extensions/)
- [Flask restplus](http://flask-restplus.readthedocs.io/en/stable/)
- [Flask-SQLalchemy](http://flask-sqlalchemy.pocoo.org/2.1/)
- [Flask-OAuth](https://pythonhosted.org/Flask-OAuth/)
- [elasticsearch-dsl](http://elasticsearch-dsl.readthedocs.io/en/latest/index.html)
- [gunicorn](http://gunicorn.org/)
- [uwsgi](https://uwsgi-docs.readthedocs.io/en/latest/)

Tutorial

- [Flask Overview](https://www.slideshare.net/maxcnunes1/flask-python-16299282)
- [In Flask we trust](http://igordavydenko.com/talks/ua-pycon-2012.pdf)



## Changelog

- Version 2.4: Fixed Link Password Error
- Version 2.3: Added PushBot and Error Pages and Updated Blacklist
- Version 2.2: Added Re captcha Validation and CSRF Protection
- Version 2.1: Addition of Google Sign In for the Project
- Version 2.0 : Deployment for Version 2 for the project
- Version 1.0 : ShortTo V1
