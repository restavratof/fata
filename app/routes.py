import datetime
from flask import render_template, flash, redirect, url_for
from google.cloud import firestore
from app import app
from app.forms import LoginForm


@app.route('/index')
@app.route('/')
def index():
    user = {'username': 'Miguel'}
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
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/sample')
def root():
    # For the sake of example, use static information to inflate the template.
    # This will be replaced with real information in later steps.
    dummy_times = [datetime.datetime(2018, 1, 1, 10, 0, 0),
                   datetime.datetime(2018, 1, 2, 10, 30, 0),
                   datetime.datetime(2018, 1, 3, 11, 0, 0),
                   ]



    # Project ID is determined by the GCLOUD_PROJECT environment variable
    # db = firestore.Client()
    # LINE BELOW SHOULD BE USED ONLY IF LINE ABOVE NOT WORKING
    db = firestore.Client.from_service_account_json("/home/dfashchanka/conf/secrets/gcp/fa-ta-307713-91d4fd3a1ad4.json")
    data_ref = db.collection(u'verses')
    docs = data_ref.stream()
    results = []

    for doc in docs:
        print(f'{doc.id} => {doc.to_dict()}')
        results.append(doc.to_dict())

    # return render_template('index.html', times=dummy_times)
    return render_template('sample.html', times=results)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
        return redirect(url_for('/index'))
    return render_template('login.html', title='Sign In', form=form)

