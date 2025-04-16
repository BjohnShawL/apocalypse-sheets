from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length, EqualTo


class RegistrationForm(FlaskForm):
    username = StringField('Username', [Length(min=4, max=20)])
    email = StringField('Email Address', [Length(min=6, max=50)])
    password = PasswordField('New Password', [
        DataRequired(),
        EqualTo('confirm', message='Passwords must match')
    ])
    confirm = PasswordField('Repeat Password')

class LoginForm(FlaskForm):
    email = StringField('Email Address', [Length(min=6, max=50)])
    password = PasswordField('Password', [DataRequired()])