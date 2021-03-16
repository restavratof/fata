from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login


class User(object):
    def __init__(self, phone, name, email):
        self.phone = phone
        self.name = name
        self.email = email
        self.psw_hash = None

    def set_password(self, password):
        self.psw_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.psw_hash, password)

    @login.user_loader
    def load_user(phone):
        return User.query.get(phone)

    @staticmethod
    def from_dict(source):
        city = User(source[u'phone'], source[u'name'], source[u'email'], source[u'psw_hash'])
        return city

    def to_dict(self):
        dest = {
            u'phone': self.phone,
            u'name': self.name,
            u'email': self.email,
            u'psw_hash': self.psw_hash
        }
        return dest

    def __repr__(self):
        return(
            f'User(\
                phone={self.phone}, \
                name={self.name},\
                email={self.email},\
                psw_hash={self.psw_hash}\
            )'
        )

# users_ref = db.collection(u'users')
# users_ref.document(u'+375291234567').set(
#     User(u'Vasya').to_dict())


class Post(object):
    def __init__(self, user_id, body, timestamp):
        self.user_id = user_id
        self.body = body
        self.timestamp = timestamp

    @staticmethod
    def from_dict(source):
        # ...
        pass

    def to_dict(self):
        # ...
        pass

    def __repr__(self):
        return(
            f'User(\
                user_id={self.user_id}, \
                body={self.body},\
                timestamp={self.timestamp}\
            )'
        )
