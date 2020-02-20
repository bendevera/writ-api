# project/server/models.py


import jwt
import datetime

from project.server import app, db, bcrypt
from sqlalchemy.dialects.postgresql.json import JSONB
import json

class User(db.Model):
    """ User Model for storing user related details """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    works = db.relationship("Work", backref="user")

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = bcrypt.generate_password_hash(
            password, app.config.get('BCRYPT_LOG_ROUNDS')
        ).decode()
        self.registered_on = datetime.datetime.now()
        self.admin = admin

    def encode_auth_token(self, user_id):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1, seconds=0),
                'iat': datetime.datetime.utcnow(),
                'sub': user_id
            }
            return jwt.encode(
                payload,
                app.config.get('SECRET_KEY'),
                algorithm='HS256'
            )
        except Exception as e:
            return e

    @staticmethod
    def decode_auth_token(auth_token):
        """
        Validates the auth token
        :param auth_token:
        :return: integer|string
        """
        try:
            payload = jwt.decode(auth_token, app.config.get('SECRET_KEY'))
            is_blacklisted_token = BlacklistToken.check_blacklist(auth_token)
            if is_blacklisted_token:
                return 'Token blacklisted. Please log in again.'
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            return 'Signature expired. Please log in again.'
        except jwt.InvalidTokenError:
            return 'Invalid token. Please log in again.'


class Work(db.Model):
    """
    Work Model for storing a piece of literary work.
    """
    __tablename__ = 'works'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    created = db.Column(db.Date, default=datetime.datetime.now())
    last_updated = db.Column(db.Date)
    newest_version = db.Column(db.Integer)
    versions = db.relationship("Version", backref="work")

    def __init__(self, user_id):
        self.user_id = user_id
        self.created = datetime.datetime.now()
        self.last_updated = self.created
        self.newest_version = 1
        first_version = Version(
            work_id=self.id, 
            number=self.newest_version, 
            data={"title":"", "text":""}
        )
        self.versions = [first_version]
    
    def new_version(self):
        print(self.newest_version)
        recent = Version.query.filter_by(
            work_id=self.id, 
            number=self.newest_version
        ).first()
        self.newest_version += 1
        new = Version(
            work_id=self.id,
            data=recent.data,
            number=self.newest_version
        )
        self.versions.append(new)
        self.last_updated = datetime.datetime.now()
        db.session.commit()
        return new

    def to_json(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "created": self.created,
            "last_updated": self.last_updated,
            "versions": [v.to_json() for v in self.versions]
        }


class Version(db.Model):
    """
    Version Model for storing every version of a work.
    """
    __tablename__ = "versions"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    work_id = db.Column(db.Integer, db.ForeignKey("works.id"))
    number = db.Column(db.Integer)
    color = db.Column(db.String)
    data = db.Column(JSONB)

    def to_json(self):
        result = self.data
        result['id'] = self.id
        result['work_id'] = self.work_id
        result['number'] = self.number
        result['color'] = self.color
        return result
    

class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)

    @staticmethod
    def check_blacklist(auth_token):
        # check whether auth token has been blacklisted
        res = BlacklistToken.query.filter_by(token=str(auth_token)).first()
        if res:
            return True
        else:
            return False
