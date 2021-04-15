from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app, abort
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app import translate_client
from app.main.forms import EditProfileForm, EmptyForm, PostForm
from app.models.user_model import User
from app.models.post_model import Post
from app.main import bp
import logging
from google.cloud import firestore
import six


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.collection(u'users').document(current_user.email).set({u'last_seen': current_user.last_seen}, merge=True)
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(user_id=current_user.email, user_name=current_user.name, body=form.post.data,
                    language=language)
        db.collection(u'posts').add(post.to_dict())
        flash(_('Your post is now live!'))
        return redirect(url_for('main.index'))
    # page = request.args.get('page', 1, type=int)
    # posts = current_user.followed_posts().paginate(
    #     page, current_app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('main.index', page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('main.index', page=posts.prev_num) \
    #     if posts.has_prev else None
    # List of posts
    # return render_template('index.html', title=_('Home'), form=form,
    #                        posts=posts.items, next_url=next_url,
    #                        prev_url=prev_url)
    posts_ref = db.collection(u'posts').where(u'user_id', u'==', current_user.email).stream()
    posts = list()
    for post_ref in posts_ref:
        logging.debug(f'post_ref={post_ref.to_dict()}')
        posts.append(Post.from_dict(post_ref.to_dict()))
    return render_template("index.html", title=_('Home'), form=form,
                           posts=posts)


@bp.route('/explore')
@login_required
def explore():
    # page = request.args.get('page', 1, type=int)
    # posts = Post.query.order_by(Post.timestamp.desc()).paginate(
    #     page, current_app.config['POSTS_PER_PAGE'], False)
    # next_url = url_for('main.explore', page=posts.next_num) \
    #     if posts.has_next else None
    # prev_url = url_for('main.explore', page=posts.prev_num) \
    #     if posts.has_prev else None
    # return render_template('index.html', title=_('Explore'),
    #                        posts=posts.items, next_url=next_url,
    #                        prev_url=prev_url)
    logging.info('-'*100)
    limit_num = current_app.config['POSTS_PER_PAGE']
    doc = request.args.get('doc', None, type=str)
    logging.info(f"IN: {doc} ({limit_num})")

    if doc is None:
        logging.info(f' *** DEFAULT ***')
        posts_ref = db.collection(u'posts').order_by(u'timestamp', direction=firestore.Query.DESCENDING) \
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
    next_url = url_for('main.explore', doc=last_doc) # if posts_ref.has_next else None
    # prev_url = url_for('explore', doc=prev_doc) # if posts_ref.has_prev else None

    return render_template("index.html", title=_('Explore'), posts=posts, next_url=next_url, prev_url=None)


@bp.route('/user/<email>')
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


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.name)
    if form.validate_on_submit():
        current_user.name = form.username.data
        current_user.about_me = form.about_me.data
        db.collection(u'users').document(current_user.email).set(current_user.to_dict())
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.name
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'), form=form)


@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
    text = request.form['text']
    target= request.form['dest_language']
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)
    logging.debug(f'result: {result}')

    return jsonify({'text': result["translatedText"] })
