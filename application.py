from app import app
from flask_debug import Debug
application = app
if __name__ == '__main__':
    Debug(app)
    app.run(host='0.0.0.0',debug=True)
