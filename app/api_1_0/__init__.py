from flask import Blueprint

api = Blueprint('api', __name__)

from . import authentication, api_user, api_blog, errors, tools
