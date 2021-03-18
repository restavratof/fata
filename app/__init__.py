from flask import Flask
from flask_login import LoginManager
from flask_mail import Mail
from google.cloud import firestore
import logging
import sys
from logging.handlers import SMTPHandler
from config import Config
from flask_bootstrap import Bootstrap
from flask_moment import Moment


app = Flask(__name__)
app.config.from_object(Config)

mail = Mail(app)
bootstrap = Bootstrap(app)
moment = Moment(app)

logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(filename)s - %(funcName)s '
                           '- %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.info(' *** Service logging configured *** ')

# db = firestore.Client.from_service_account_json(Config.GCP_CREDENTIALS)
db = firestore.Client()
login = LoginManager(app)
login.login_view = 'login'


if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure',
            credentials=auth, secure=secure)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


from app import routes, errors
from app.models import user_model, post_model


