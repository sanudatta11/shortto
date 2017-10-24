from wtforms import Form, BooleanField, StringField, PasswordField, validators
from wtforms.validators import DataRequired


class Url_form(Form):
    from_url = StringField('From',validators=[DataRequired()])
    to_url = StringField('To')