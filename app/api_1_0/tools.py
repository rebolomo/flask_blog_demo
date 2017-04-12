from . import api
from ..models import User, Blog, Role
from .. import db
from . import authentication
import json
from app import logger

# clear db
@api.route('/clear-db-all/', methods=['POST'])
@authentication.login_exempt
def clear_db_all():
    Blog.query.delete()
    User.query.delete()
    Role.query.delete()

    db.session.commit()
    ret = {}
    return json.dumps(ret)