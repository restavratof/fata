import datetime
from flask import request
from flask import render_template, flash, redirect, url_for, abort
from flask_login import current_user, login_user, logout_user, login_required
from google.cloud import firestore
from werkzeug.urls import url_parse
from app import app
from app import db
from app.forms import LoginForm
from app.forms import RegistrationForm
from app.forms import EditProfileForm
from app.forms import PostForm
from app.forms import ResetPasswordRequestForm
from app.forms import ResetPasswordForm
from app.models.user_model import User
from app.models.post_model import Post
from app.email import send_password_reset_email

import logging
from datetime import datetime


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    # New post form
    form = PostForm()
    if form.validate_on_submit():
        post = Post(user_id=current_user.email, body=form.post.data)
        db.collection(u'posts').add(post.to_dict())
        flash('Your post is now live!')
        return redirect(url_for('index'))
    # List of posts
    posts_ref = db.collection(u'posts').where(u'user_id', u'==', current_user.email).stream()
    posts = list()
    for post_ref in posts_ref:
        logging.debug(f'post_ref={post_ref.to_dict()}')
        posts.append(Post.from_dict(post_ref.to_dict()))
    return render_template("index.html", title='Home Page', form=form,
                           posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
            flash('Invalid username or password')
            return redirect(url_for('login'))
        logging.debug(f"check point 1")
        login_user(user, remember=form.remember_me.data)
        logging.debug(f"check point 2")
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        logging.debug(f"check point 3")
        return redirect(next_page)
    logging.debug(f"check point 4")
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # logging.debug(f"phone={form.phone.data}")
        # logging.debug(f"name={form.username.data}")
        # logging.debug(f"email={form.email.data}")
        # logging.debug(f"psw={form.password.data}")
        user = User(phone=form.phone.data, name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.collection(u'users').document(user.email).set(user.to_dict())
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<email>')
@login_required
def user(email):
    logging.debug(f'IN: {email}')
    user_dict = db.collection(u'users').document(email).get().to_dict()
    logging.debug(f"user_dict={user_dict}")
    if user_dict is None:
        abort(404)

    user = User.from_dict(user_dict)
    logging.debug(f"user={user}")

    # List of posts
    posts_ref = db.collection(u'posts').where(u'user_id', u'==', email).stream()
    posts = list()
    for post_ref in posts_ref:
        logging.debug(f'post_ref={post_ref.to_dict()}')
        posts.append(Post.from_dict(post_ref.to_dict()))
    return render_template('user.html', user=user, posts=posts)

@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.collection(u'users').document(current_user.email).set({u'last_seen': current_user.last_seen}, merge=True)
        # users_ref = db.collection(u'users').where(u'last_seen', u'==', current_user.last_seen).limit(1).stream()
        # for usr_ref in users_ref:
        #     usr_ref.set({u'last_seen': current_user.last_seen}, merge=True)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.name)
    if form.validate_on_submit():
        current_user.name = form.username.data
        current_user.about_me = form.about_me.data
        db.collection(u'users').document(current_user.email).set(current_user.to_dict())

        # db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@app.route('/explore')
@login_required
def explore():
    logging.info('-'*100)
    limit_num = app.config['POSTS_PER_PAGE']
    doc = request.args.get('doc', None, type=str)
    logging.info(f"IN: {doc} ({limit_num})")

    if doc is None:
        logging.info(f' *** DEFAULT ***')
        posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING)\
            .limit(limit_num).stream()
    else:
        logging.info(f' *** PAGINATED ***')

        # date_time_obj = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f%z')
        # logging.info(f"date_time_obj: {date_time_obj}")
        # posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING) \
        #     .start_after({u'timestamp': date_time_obj}).limit(limit_num).stream()
        doc_ref = db.collection(u'posts').document(doc).get()
        posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING) \
            .start_after(doc_ref).limit(limit_num).stream()

    # logging.debug(f'LIST: {[x.to_dict() for x in posts_ref]}')

    posts = list()
    last_doc = None
    for post_ref in posts_ref:
        logging.info(f'post_ref={post_ref.to_dict()}')
        posts.append(Post.from_dict(post_ref.to_dict()))
        last_doc = post_ref.id

    logging.info(f'posts={posts}')
    # last_doc = posts[-1].id
    # logging.info(f'last_doc={last_doc}')

    # posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', doc=last_doc) # if posts_ref.has_next else None
    # prev_url = url_for('explore', doc=prev_doc) # if posts_ref.has_prev else None

    return render_template("index.html", title='Explore', posts=posts, next_url=next_url, prev_url=None)


    # posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING).stream()
    # posts = list()
    # for p_ref in posts_ref:
    #     logging.info(f'post_ref={p_ref.to_dict()}')
    #     posts.append(Post.from_dict(p_ref.to_dict()))
    # return render_template('index.html', title='Explore', posts=posts)



@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        logging.info(f"email={form.email.data}")
        user_dict = db.collection(u'users').document(form.email.data).get().to_dict()
        logging.info(f"user_dict={user_dict}")
        if user_dict:
            logging.info(f'Sending email...')
            user = User.from_dict(user_dict)
            send_password_reset_email(user)
        flash('If user with such email was registered. '
              'Application will send the instructions to reset your password to the email.')
        return redirect(url_for('login'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.collection(u'users').document(user.email).set(user.to_dict())
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)





