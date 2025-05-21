from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.posts import bp
from app.posts.forms import PostForm
from app.models import Post
from app.extensions import db
from werkzeug.utils import secure_filename
import os
from flask import current_app

@bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            author=current_user
        )
        
        # Gestione upload file
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            upload_path = os.path.join(current_app.root_path, 'static/uploads')  # Modificato qui
            os.makedirs(upload_path, exist_ok=True)
            filepath = os.path.join(upload_path, filename)
            form.image_file.data.save(filepath)
            post.image_path = f"uploads/{filename}"  # Percorso relativo alla cartella static
        
        # Gestione URL immagine
        if form.image_url.data:
            post.image_url = form.image_url.data
        
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
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        
        # Gestione aggiornamento immagini
        if form.image_file.data:
            filename = secure_filename(form.image_file.data.filename)
            upload_path = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_path, exist_ok=True)
            filepath = os.path.join(upload_path, filename)
            form.image_file.data.save(filepath)
            post.image_path = f"uploads/{filename}"
            post.image_url = None  # Resetta URL se si carica un file
        
        if form.image_url.data:
            post.image_url = form.image_url.data
            post.image_path = None  # Resetta file se si inserisce un URL
        
        db.session.commit()
        flash('Il tuo post è stato aggiornato!', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        # Pre-carica i valori delle immagini se esistenti
        form.image_url.data = post.image_url
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