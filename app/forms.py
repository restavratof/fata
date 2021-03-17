from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models.user_model import User
from app import db
import logging


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    phone = StringField('Phone', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_phone(self, phone):
        logging.debug(f'IN: {phone}')
        users = db.collection(u'users').where(u'phone', u'==', phone.data).stream()
        logging.debug(f'users={users}')
        for doc in users:
            logging.debug(f'{doc.id} => {doc.to_dict()}')
            raise ValidationError('Please use a different phone number.')

    def validate_email(self, email):
        logging.debug(f'IN: {email}')
        users = db.collection(u'users').where(u'email', u'==', email.data).stream()
        logging.debug(f'users={users}')
        for doc in users:
            logging.debug(f'{doc.id} => {doc.to_dict()}')
            raise ValidationError('Please use a different email address.')

    def validate_username(self, username):
        logging.debug(f'IN: {username}')
        users = db.collection(u'users').where(u'name', u'==', username.data).stream()
        logging.debug(f'users={users}')
        for doc in users:
            logging.debug(f'{doc.id} => {doc.to_dict()}')
            raise ValidationError('Please use a different username.')


class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            users = db.collection(u'users').where(u'name', u'==', username.data).stream()
            logging.debug(f'users={users}')
            for doc in users:
                logging.debug(f'{doc.id} => {doc.to_dict()}')
                raise ValidationError('Please use a different username.')


class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')


