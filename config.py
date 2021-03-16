import os


class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    GCP_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS') or \
                      "/home/dfashch/cfg/gcp/fa-ta-307713-fcea29ce54c7.json"
