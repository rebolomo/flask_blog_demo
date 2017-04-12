from flask import jsonify, current_app
from app.exceptions import ValidationError
from . import api
from app import logger

def bad_request(errorcode):
    errorcode = str(errorcode)
    conf = current_app.config['CONF']

    response = json.loads({'errorcode': errorcode, 'message': conf['errorcode'][errorcode]['desc']})
    response.status_code = 200
    return response

@api.errorhandler(ValidationError)
def validation_error(e):
    return bad_request(e.args[0])
