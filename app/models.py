from datetime import datetime
import hashlib
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from flask import current_app, request, url_for, g, jsonify
from flask.ext.login import UserMixin, AnonymousUserMixin
from . import db, login_manager, logger
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
import json
import time

class Permission:
    FOLLOW = 0x01
    COMMENT = 0x02
    CREATE_BLOG = 0x04
    MODERATE_COMMENTS = 0x08
    ADMINISTER = 0x80

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    @staticmethod
    def insert_roles():
        roles = {
            'User': (Permission.FOLLOW |
                     Permission.COMMENT |
                     Permission.CREATE_BLOG, True),
            'Moderator': (Permission.FOLLOW |
                          Permission.COMMENT |
                          Permission.CREATE_BLOG |
                          Permission.MODERATE_COMMENTS, False),
            'Administrator': (0xff, False)
        }
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.permissions = roles[r][0]
            role.default = roles[r][1]
            db.session.add(role)
        db.session.commit()

    def __repr__(self):
        return '<Role %r>' % self.name

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique=True, index=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    password_hash = db.Column(db.String(128))
    confirmed = db.Column(db.Boolean, default=False)
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    about_me = db.Column(db.Text())
    created_time = db.Column(db.Integer, default=time.time())
    last_seen = db.Column(db.Integer, default=time.time())

    @staticmethod
    def register_admin():
        r = Role.query.filter_by(name='Administrator').first()
        u = User(username=current_app.config['DEFAULT_ADMIN_NAME'],
                 password=current_app.config['DEFAULT_PASSWORD_FOR_USER'],
                 role=r, confirmed=True)
        db.session.add(u)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()

    @staticmethod
    def clear():        
        User.query.delete()
        Blog.query.delete()
   
        db.session.commit()

    @staticmethod
    def generate_fake(count=100):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py

        seed()
        for i in range(count):
            u = User(email=forgery_py.internet.email_address(),
                     username=forgery_py.internet.user_name(True),
                     password=forgery_py.lorem_ipsum.word(),
                     confirmed=True,
                     name=forgery_py.name.full_name(),
                     location=forgery_py.address.city(),
                     about_me=forgery_py.lorem_ipsum.sentence(),
                     member_since=forgery_py.date.date(True))
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()

    def to_json(self):
        json_user = {
            #'url': url_for('api.get_post', id=self.id, _external=True),
            'username': self.username,
            'created_time': self.created_time,
            'last_seen': self.last_seen,

            #'posts': url_for('api.get_user_posts', id=self.id, _external=True),
            #'post_count': self.posts.count(),
            'id' : self.id
        }
        return json_user

    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(permissions=0xff).first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_confirmation_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id})

    #   email confirm
    def confirm(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id})

    def reset_password(self, token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('reset') != self.id:
            return False
        self.password = new_password
        db.session.add(self)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'change_email': self.id, 'new_email': new_email})

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        db.session.add(self)
        return True

    def can(self, permissions):
        return self.role is not None and \
               (self.role.permissions & permissions) == permissions

    def is_administrator(self):
        return self.can(Permission.ADMINISTER)

    def ping(self):
        self.last_seen = time.time()
        db.session.add(self)

    # ...
    def generate_auth_token(self, expiration):
        s = Serializer(current_app.config['SECRET_KEY'],
                       expires_in=expiration)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def __repr__(self):
        return '<User %r>' % self.username


class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class Blog(db.Model):
    __tablename__ = 'blogs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Unicode(32), nullable=False)
    content = db.Column(db.Unicode(120))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    created_time = db.Column(db.Integer, default=time.time())

    def __repr__(self):
        return '<Blog %r>' % self.title

    @staticmethod
    def get(id):
        return Blog.query.filter(Blog.id == id).first()

    def to_json(self):
        json_post = {
            'id' : self.id,
            'title': self.title,
            'content': self.content,
            'user_id' : self.user_id,
        }
        return json_post

    def from_json(json_string):
        p_data = json.loads(json_string)
        blog = Blog(title = p_data['title'],
                    content = p_data['content'])

        return blog
    def from_dict(params):
        p_data = params
        logger.info(p_data)
        blog = Blog(title = p_data['title'],
                    content = p_data['content'],
                    user_id=p_data['user_id'])

        return blog