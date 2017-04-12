from flask.ext.wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

from flask.ext.babel import lazy_gettext


class LoginForm(Form):
    name = StringField(lazy_gettext('Username'), validators=[Required(), Length(1, 64)])
    password = PasswordField(lazy_gettext('Password'), validators=[Required()])
    remember_me = BooleanField(lazy_gettext('Keep me logged in'))
    submit = SubmitField(lazy_gettext('Log In'))


class RegistrationForm(Form):
    email = StringField(lazy_gettext('Email'), validators=[Required(), Length(1, 64),
                                                           Email()])
    username = StringField(lazy_gettext('Username'), validators=[
        Required(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                                          lazy_gettext(
                                              'Usernames must have only letters, numbers, dots or underscores'))])
    password = PasswordField(lazy_gettext('Password'), validators=[
        Required(), EqualTo('password2', message=lazy_gettext('Passwords must match.'))])
    password2 = PasswordField(lazy_gettext('Confirm password'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Register'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_gettext('Email already registered.'))

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError(lazy_gettext('Username already in use.'))


class ChangePasswordForm(Form):
    old_password = PasswordField(lazy_gettext('Old password'), validators=[Required()])
    password = PasswordField(lazy_gettext('New password'), validators=[
        Required(), EqualTo('password2', message=lazy_gettext('Passwords must match'))])
    password2 = PasswordField(lazy_gettext('Confirm new password'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Update Password'))


class PasswordResetRequestForm(Form):
    email = StringField(lazy_gettext('Email'), validators=[Required(), Length(1, 64),
                                                           Email()])
    submit = SubmitField(lazy_gettext('Reset Password'))


class PasswordResetForm(Form):
    email = StringField(lazy_gettext('Email'), validators=[Required(), Length(1, 64),
                                                           Email()])
    password = PasswordField(lazy_gettext('New Password'), validators=[
        Required(), EqualTo('password2', message=lazy_gettext('Passwords must match'))])
    password2 = PasswordField(lazy_gettext('Confirm password'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Reset Password'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first() is None:
            raise ValidationError(lazy_gettext('Unknown email address.'))


class ChangeEmailForm(Form):
    email = StringField(lazy_gettext('New Email'), validators=[Required(), Length(1, 64),
                                                 Email()])
    password = PasswordField(lazy_gettext('Password'), validators=[Required()])
    submit = SubmitField(lazy_gettext('Update Email Address'))

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError(lazy_gettext('Email already registered.'))