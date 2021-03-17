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
from app.models.user_model import User
from app.models.post_model import Post


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
        logging.debug(f"user_dict={user_dict}")
        user = User.from_dict(user_dict)
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
    doc = request.args.get('doc', None, type=dict)
    logging.debug(f'IN: {doc}')
    if doc is None:
        posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING)\
            .limit(app.config['POSTS_PER_PAGE']).stream()
    else:
        posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING) \
            .start_at(doc).limit(app.config['POSTS_PER_PAGE']).stream()

    next_doc = list(posts_ref)[-1]
    prev_doc = list(posts_ref)[0]
    logging.debug(f'next_doc={next_doc.to_dict()}')
    logging.debug(f'prev_doc={prev_doc.to_dict()}')

    posts = list()
    for post_ref in posts_ref:
        logging.debug(f'post_ref={post_ref.to_dict()}')
        posts.append(Post.from_dict(post_ref.to_dict()))

    # posts = Post.query.order_by(Post.timestamp.desc()).paginate(page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('explore', doc=next_doc.to_dict()) # if posts_ref.has_next else None
    prev_url = url_for('explore', doc=prev_doc.to_dict()) # if posts_ref.has_prev else None

    return render_template("index.html", title='Explore', posts=posts.items, next_url=next_url, prev_url=prev_url)


    # posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING).stream()
    # posts = list()
    # for p_ref in posts_ref:
    #     logging.debug(f'post_ref={p_ref.to_dict()}')
    #     posts.append(Post.from_dict(p_ref.to_dict()))
    # return render_template('index.html', title='Explore', posts=posts)




