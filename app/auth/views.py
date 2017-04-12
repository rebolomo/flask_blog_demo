from flask import render_template, redirect, request, url_for, flash
from flask.ext.login import login_user, logout_user, login_required, \
    current_user
from flask.ext.babel import gettext

from . import auth
from .. import db
from ..models import User
from app.tools.custom_email import send_email
from .forms import LoginForm, RegistrationForm, ChangePasswordForm, \
    PasswordResetRequestForm, PasswordResetForm, ChangeEmailForm


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
                and request.endpoint[:5] != 'auth.' \
                and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('blog.index'))
    return render_template('auth/unconfirmed.html')


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.name.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('blog.index'))
        flash('Invalid username or password.')
    return render_template('default_form.html', form=form, form_title = gettext('Login'))



@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash(gettext('You have been logged out.'))
    return redirect(url_for('blog.index'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data,
                    password=form.password.data,
                    confirmed=True, )
        db.session.add(user)
        db.session.commit()
        # REBOL todo, email feature later
        """
        token = user.generate_confirmation_token()
        send_email(user.email, 'Confirm Your Account',
                   'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        """
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('blog.index'))
    if current_user.confirm(token):
        flash(gettext('You have confirmed your account. Thanks!'))
    else:
        flash(gettext('The confirmation link is invalid or has expired.'))
    return redirect(url_for('blog.index'))


@auth.route('/confirm')
@login_required
def resend_confirmation():
    token = current_user.generate_confirmation_token()
    send_email(current_user.email, 'Confirm Your Account',
               'auth/email/confirm', user=current_user, token=token)
    flash(gettext('A new confirmation email has been sent to you by email.'))
    return redirect(url_for('blog.index'))


@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            flash(gettext('Your password has been updated.'))
            return redirect(url_for('shop.index'))
        else:
            flash(gettext('Invalid password.'))
    return render_template("auth/change_password.html", form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    if not current_user.is_anonymous:
        return redirect(url_for('blog.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            token = user.generate_reset_token()
            send_email(user.email, 'Reset Your Password',
                       'auth/email/reset_password',
                       user=user, token=token,
                       next=request.args.get('next'))
        flash(gettext('An email with instructions to reset your password has been sent to you.'))
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('blog.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            return redirect(url_for('blog.index'))
        if user.reset_password(token, form.password.data):
            flash(gettext('Your password has been updated.'))
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('blog.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change-email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_email(new_email, gettext('Confirm your email address'),
                       'auth/email/change_email',
                       user=current_user, token=token)
            flash(gettext('An email with instructions to confirm your new email '
                  'address has been sent to you.'))
            return redirect(url_for('blog.index'))
        else:
            flash(gettext('Invalid email or password.'))
    return render_template("auth/change_email.html", form=form)


@auth.route('/change-email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        flash(gettext('Your email address has been updated.'))
    else:
        flash(gettext('Invalid request.'))
    return redirect(url_for('blog.index'))
