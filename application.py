from app import app
import os
application = app
if __name__ == '__main__':
    if os.environ.get('ENVIRONMENT') == "DEVELOPEMENT":
        app.run(host='0.0.0.0',debug=False)
    else:
        app.run(threaded=True,host='0.0.0.0',debug=False,port='80')