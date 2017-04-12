from flask.ext.wtf import Form
from wtforms import SelectField, StringField, TextAreaField, BooleanField, SelectField
from wtforms.validators import Required, Length,Email, Regexp
from wtforms import ValidationError, IntegerField
from wtforms import FieldList
from wtforms import Form as NoCsrfForm
from wtforms.fields import StringField, FormField, SubmitField, FileField
from ..models import Blog, Role, User
from flask.ext.login import current_user
from flask.ext.babel import lazy_gettext

from app import logger

# excel import
class ExcelImportForm(Form):
    excel = FileField(lazy_gettext('Excel file'))
    submit = SubmitField(lazy_gettext('Submit'))

class NameForm(Form):
    name = StringField(lazy_gettext('What is your name?'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Submit'))


class EditProfileForm(Form):
    name = StringField(lazy_gettext('Real name'), validators=[Length(0, 64)])
    location = StringField(lazy_gettext('Location'), validators=[Length(0, 64)])
    about_me = TextAreaField(lazy_gettext('About me'))
    submit = SubmitField(lazy_gettext('Submit'))


class EditProfileAdminForm(Form):
    email = StringField(lazy_gettext('Email'), validators=[Required(), Length(1, 64),
                                                           Email()])
    username = StringField(lazy_gettext('Username'), validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          lazy_gettext(
                                              'Usernames must have only letters, numbers, dots or underscores'))])
    confirmed = BooleanField(lazy_gettext('Confirmed'))
    role = SelectField(lazy_gettext('Role'), coerce=int)
    name = StringField(lazy_gettext('Real name'), validators=[Length(0, 64)])
    location = StringField(lazy_gettext('Location'), validators=[Length(0, 64)])
    about_me = TextAreaField(lazy_gettext('About me'))
    submit = SubmitField(lazy_gettext('Submit'))

    def __init__(self, user, *args, **kwargs):
        super(EditProfileAdminForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        if field.data != self.user.email and \
                User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_gettext('Email already registered.'))

    def validate_username(self, field):
        if field.data != self.user.username and \
                User.query.filter_by(username=field.data).first():
            raise ValidationError(lazy_gettext('Username already in use.'))