from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired, Email


class Url_form(Form):
    from_url = StringField('From',validators=[DataRequired()])
    to_url = StringField('To')

class Login(Form):
    email = StringField('email',validators=[DataRequired(),Email()])
    password = StringField('password', validators=[DataRequired()])
