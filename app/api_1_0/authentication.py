from flask import g, jsonify, request, current_app
from flask.ext.httpauth import HTTPBasicAuth
from ..models import User, AnonymousUser
from . import api
from .errors import bad_request

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(username_or_token, password):
    if username_or_token == '':
        g.current_user = AnonymousUser()
        #return True
        # REBOL note, anonymous can't access
        return False
    if password == '':
        g.current_user = User.verify_auth_token(username_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(username=username_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return bad_request(INVALID_CREDENTIALS)


#@api.before_request
#@auth.login_required
def before_request():
    print('testttttttttt')
    #if not g.current_user.is_anonymous and \
    #        not g.current_user.confirmed:
    #    return forbidden('Unconfirmed account')

def login_exempt(f):
    f.login_exempt = True
    return f

# a dummy callable to execute the login_required logic
login_required_dummy_view = auth.login_required(lambda: None)

@api.before_request
def default_login_required():
    # exclude 404 errors and static routes
    # uses split to handle blueprint static routes as well
    if not request.endpoint or request.endpoint.rsplit('.', 1)[-1] == 'static':
        return

    view = current_app.view_functions[request.endpoint]
    # REBOL note, register don't need login required, use this decorator for register route.
    if getattr(view, 'login_exempt', False):
        return

    return login_required_dummy_view()