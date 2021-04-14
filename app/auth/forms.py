from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from flask_babel import _, lazy_gettext as _l
from app.models.user_model import User
from app import db
import logging


class LoginForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    remember_me = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))


class RegistrationForm(FlaskForm):
    phone = StringField(_l('Phone'), validators=[DataRequired()])
    username = StringField(_l('Username'), validators=[DataRequired()])
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField(_l('Register'))

    def validate_phone(self, phone):
        logging.debug(f'IN: {phone}')
        users = db.collection(u'users').where(u'phone', u'==', phone.data).stream()
        logging.debug(f'users={users}')
        for doc in users:
            logging.debug(f'{doc.id} => {doc.to_dict()}')
            raise ValidationError(_('Please use a different phone number.'))

    def validate_username(self, username):
        logging.debug(f'IN: {username}')
        users = db.collection(u'users').where(u'name', u'==', username.data).stream()
        logging.debug(f'users={users}')
        for doc in users:
            logging.debug(f'{doc.id} => {doc.to_dict()}')
            raise ValidationError(_('Please use a different username.'))

    def validate_email(self, email):
        logging.debug(f'IN: {email}')
        users = db.collection(u'users').where(u'email', u'==', email.data).stream()
        logging.debug(f'users={users}')
        for doc in users:
            logging.debug(f'{doc.id} => {doc.to_dict()}')
            raise ValidationError(_('Please use a different email address.'))


class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    password2 = PasswordField(
        _l('Repeat Password'), validators=[DataRequired(),
                                           EqualTo('password')])
    submit = SubmitField(_l('Request Password Reset'))
