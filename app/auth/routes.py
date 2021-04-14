from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_babel import _
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models.user_model import User
from app.auth.email import send_password_reset_email
import logging


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Get user document from collection
        user_dict = db.collection(u'users').document(form.email.data).get().to_dict()
        if user_dict is not None:
            logging.debug(f"user_dict={user_dict}")
            user = User.from_dict(user_dict)
        else:
            user = user_dict
        logging.debug(f"user={user}")

        if user is None or not user.check_password(form.password.data):
            logging.debug(f"Invalid username or password")
            flash(_('Invalid username or password'))
            return redirect(url_for('auth.login'))
        logging.debug(f"check point 1")
        login_user(user, remember=form.remember_me.data)
        logging.debug(f"check point 2")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        logging.debug(f"check point 3")
        return redirect(next_page)
    logging.debug(f"check point 4")
    return render_template('auth/login.html', title=_('Sign In'), form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        logging.debug(f"phone={form.phone.data}")
        logging.debug(f"name={form.username.data}")
        logging.debug(f"email={form.email.data}")
        logging.debug(f"psw={form.password.data}")
        user = User(phone=form.phone.data, name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.collection(u'users').document(user.email).set(user.to_dict())
        flash(_('Congratulations, you are now a registered user!'))
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title=_('Register'), form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        logging.info(f"email={form.email.data}")
        user_dict = db.collection(u'users').document(form.email.data).get().to_dict()
        logging.info(f"user_dict={user_dict}")
        if user_dict:
            logging.info(f'Sending email...')
            user = User.from_dict(user_dict)
            send_password_reset_email(user)
        flash(_('If user with such email was registered. '
              'Application will send the instructions to reset your password to the email.'))
        return redirect(url_for('login'))
    return render_template('auth/reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.collection(u'users').document(user.email).set(user.to_dict())
        flash(_('Your password has been reset.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)
