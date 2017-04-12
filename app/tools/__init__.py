from flask import Blueprint

tool = Blueprint('tool', __name__)

from . import custom_email, excel_config, mylogger, tools