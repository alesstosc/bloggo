from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.posts import bp
from app.posts.forms import PostForm
from app.models import Post
from app.extensions import db

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash('Il tuo post è stato creato!', 'success')
        return redirect(url_for('main.index'))
    return render_template('create_post.html', title='Nuovo Post', form=form)

@bp.route('/<int:post_id>')
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('view_post.html', title=post.title, post=post)

@bp.route('/<int:post_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403) # Accesso negato se non è l'autore
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Il tuo post è stato aggiornato!', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('edit_post.html', title='Modifica Post', form=form, post=post)

@bp.route('/<int:post_id>/delete', methods=['POST']) # Usare POST per azioni distruttive
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Il tuo post è stato eliminato!', 'success')
    return redirect(url_for('main.index'))