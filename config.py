import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GCP_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or \
                      "/home/dfashchanka/conf/secrets/gcp/fa-ta-307713-91d4fd3a1ad4.json"
