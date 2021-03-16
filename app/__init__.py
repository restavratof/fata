from flask import Flask
from config import Config
from flask_login import LoginManager
from google.cloud import firestore


app = Flask(__name__)
app.config.from_object(Config)

db = firestore.Client.from_service_account_json(Config.GCP_CREDENTIALS)
login = LoginManager(app)
login.login_view = 'login'


from app import routes, models


