from flask import render_template, redirect, url_for, abort, flash
from flask.ext.login import login_required, current_user
from flask.ext.babel import gettext

from . import blog
from .forms_blog import BlogForm
from .. import db
from ..models import Blog


# ============================================

# create a blog
@blog.route('/blog/add', methods=['GET', 'POST'])
@login_required
def blog_add():
    form = BlogForm(user=current_user)
    if form.validate_on_submit():
        blog = Blog(title=form.title.data, content=form.content.data, user_id=current_user.id)
        db.session.add(blog)
        db.session.commit()

        return redirect(url_for('blog.blog_list'))

    return render_template('default_form.html', form=form, form_title=gettext('Add Blog'))


# edit a blog
@blog.route('/blog/edit/<int:blog_id>', methods=['GET', 'POST'])
@login_required
def blog_edit(blog_id):
    blog = Blog.query.get(blog_id)
    if blog is None:
        flash(gettext('Invalid blog id'))
        abort(403)

    if current_user.id != blog.user_id:
        flash(gettext('You can\'t access to this blog'))
        abort(403)
    form = BlogForm(user=current_user, edit=True, blog_id=blog_id)
    if form.validate_on_submit():
        blog.title = form.title.data
        blog.content = form.content.data

        db.session.add(blog)
        db.session.commit()
        flash(gettext('The blog has been updated.'))
        return redirect(url_for('blog.blog_list'))
    form.title.data = blog.title
    form.content.data = blog.content

    return render_template('default_form.html', form=form, form_title=gettext('Edit Blog'))

# blog list of a user
@blog.route("/blog/list", methods=["GET", "POST"])
@login_required
def blog_list():
    blogs = Blog.query.filter_by(user_id=current_user.id).all()
    # REBOL todo, pager
    return render_template('blog/blog_list.html', blogs=blogs)
