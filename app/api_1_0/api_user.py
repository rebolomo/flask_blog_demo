from flask import jsonify, request, current_app, url_for, g
from . import api
from ..models import Blog
from .. import db
from .errors import bad_request
from flask.ext.httpauth import HTTPBasicAuth
from . import authentication
import json
from app import logger

auth = HTTPBasicAuth()

# login api
@api.route('/user/login', methods=['POST'])
# @authentication.login_exempt
def login():
    # username = request.json.get('username')
    ret = {}
    if g.current_user.is_anonymous or g.token_used:
        ret['errorcode'] = 1001
        return jsonify(ret)
        # return unauthorized('Invalid credentials')

    ret['errorcode'] = 0
    ret['access_token'] = g.current_user.generate_auth_token(
        expiration=3600).decode('ascii')
    ret['expiration'] = 3600
    logger.info(g.current_user.username)
    user = User.query.filter_by(username=g.current_user.username).first()

    ret['user'] = user.to_json()
    
    return jsonify(ret)

# learn from http://blog.miguelgrinberg.com/post/restful-authentication-with-flask
# register api
@api.route('/user/register', methods=['POST'])
# REBOL note, avoid using before_request here
@authentication.login_exempt
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        return bad_request(ACCOUNT_OR_PASSWORD_EMPTY)  # missing arguments

    if User.query.filter_by(username=username).first() is not None:
        return bad_request(ACCOUNT_ALREADY_REGISTERED)  # existing user

    user = User(username=username, password=password,
                confirmed=True, )

    db.session.add(user)
    db.session.commit()
    ret = {}
    account = dict()
    account['username'] = username
    account['fullname'] = username
    account['state'] = user.confirmed
    account['id'] = user.id
    #account['fb_id'] = 0
    ret['item'] = account
    ret['access_token'] = user.generate_auth_token(
        expiration=3600).decode('utf-8')

    return json.dumps(account), 200, {'Location': url_for('api.get_user', id=user.id, _external=True)}

@api.route('user/profile', methods=['GET'])
#@authentication.login_exempt
def get_user():
    ret = dict()
    ret['item'] = g.current_user.to_json()
    return jsonify(ret)
