import datetime
from flask import render_template, flash, redirect, url_for
from flask import request
from werkzeug.urls import url_parse
from app import app
from app.forms import LoginForm
from config import Config
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from app import db
from app.forms import RegistrationForm


@app.route('/index')
@app.route('/')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
    return render_template("index.html", title='Home Page', posts=posts)


@app.route('/sample')
def sample():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]



    # Project ID is determined by the GCLOUD_PROJECT environment variable
    # db = firestore.Client()
    # LINE BELOW SHOULD BE USED ONLY IF LINE ABOVE NOT WORKING
    # db = firestore.Client.from_service_account_json(Config.GCP_CREDENTIALS)
    data_ref = db.collection(u'verses')
    docs = data_ref.stream()
    results = []

    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')
        results.append(doc.to_dict())

    return render_template('sample.html', times=results)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        # Get user document from collection
        user = db.collection(u'users').document(form.username.data).get().to_dict()
        print(f"user={user}")

        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
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
        print(f"phone={form.phone.data}")
        print(f"name={form.username.data}")
        print(f"email={form.email.data}")
        print(f"psw={form.password.data}")

        user = User(phone=form.phone.data, name=form.username.data, email=form.email.data)
        user.set_password(form.password.data)

        db.collection(u'users').document(form.phone.data).set(user.to_dict())
        # db.session.add(user)
        # db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

