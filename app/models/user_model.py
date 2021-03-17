from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login, db
import logging
from hashlib import md5


class User(UserMixin, object):
    def __init__(self, phone, name, email, psw_hash = None, about_me = None, last_seen = None):
        self.id = email
        self.phone = phone
        self.name = name
        self.email = email
        self.psw_hash = psw_hash
        self.about_me = about_me
        self.last_seen = last_seen

    def set_password(self, password):
        self.psw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.psw_hash, password)

    @staticmethod
    def from_dict(source):
        logging.debug(f"IN: {source}")
        user = User(source[u'phone'], source[u'name'], source[u'email'], source[u'psw_hash'])

        if u'about_me' in source:
            user.about_me = source[u'about_me']

        if u'last_seen' in source:
            user.last_seen = source[u'last_seen']

        logging.debug(f"OUT: {user}")
        return user

    def to_dict(self):
        logging.debug(f"IN: {self}")
        result = {
            u'phone': self.phone,
            u'name': self.name,
            u'email': self.email,
            u'psw_hash': self.psw_hash,
            u'about_me': self.about_me,
            u'last_seen': self.last_seen
        }
        logging.debug(f"OUT: {result}")
        return result

    def __repr__(self):
        return(
            f'User(\
                phone={self.phone}, \
                name={self.name},\
                email={self.email},\
                psw_hash={self.psw_hash},\
                about_me={self.about_me},\
                last_seen={self.last_seen}\
            )'
        )

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'


@login.user_loader
def load_user(id):
    user_ref = db.collection(u'users').document(id).get().to_dict()
    if user_ref is not None:
        return User.from_dict(user_ref)
    return user_ref