import logging
from datetime import datetime
from hashlib import md5


class Post(object):
    def __init__(self, user_id, user_name, body, language, timestamp=datetime.utcnow()):
        self.user_id = user_id
        self.user_name = user_name
        self.body = body
        self.timestamp = timestamp
        self.language = language


    @staticmethod
    def from_dict(source):
        logging.debug(f"IN: {source}")
        post = Post(source[u'user_id'], source[u'user_name'], source[u'body'], source[u'timestamp'])
        # if u'about_me' in source:
        #     user.about_me = source[u'about_me']
        logging.debug(f"OUT: {post}")
        return post

    def to_dict(self):
        logging.debug(f"IN: {self}")
        result = {
            u'user_id': self.user_id,
            u'user_name': self.user_name,
            u'body': self.body,
            u'timestamp': self.timestamp
        }
        logging.debug(f"OUT: {result}")
        return result

    def __repr__(self):
        return(
            f'User(\
                user_id={self.user_id}, \
                user_name={self.user_name}, \
                body={self.body},\
                timestamp={self.timestamp}\
            )'
        )

    def user_avatar(self, size):
        digest = md5(self.user_id.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'