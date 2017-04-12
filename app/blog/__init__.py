from flask import Blueprint

blog = Blueprint('blog', __name__)

from . import views, views_blog, errors
from ..models import Permission

@blog.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
