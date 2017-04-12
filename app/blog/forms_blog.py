from flask.ext.wtf import Form
from wtforms import SelectField, StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length,Email, Regexp
from wtforms import ValidationError, IntegerField
from wtforms import FieldList
from wtforms import Form as NoCsrfForm
from wtforms.fields import StringField, FormField, SubmitField, FileField
from ..models import Role, User, Blog
from flask.ext.login import current_user
from flask.ext.babel import lazy_gettext

from app import logger

class BlogForm(Form):
    title = StringField(lazy_gettext('Blog title'), validators=[Required(), Length(1, 64)])
    content = StringField(lazy_gettext('Blog content'), validators=[Required(), Length(1, 64)])
    submit = SubmitField(lazy_gettext('Submit'))
    delete = SubmitField(lazy_gettext('Delete'))