from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user
from app.posts import bp
from app.posts.forms import PostForm
from app.models import Post
from app.extensions import db
from werkzeug.utils import secure_filename
import os
from flask import current_app
from PIL import Image

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
            upload_path = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_path, exist_ok=True)
            # Chiama save_picture per ridimensionare e salvare l'immagine
            try:
                filename = save_picture(form.image_file.data, upload_path, form.image_file.data.filename)
                if filename:
                    post.image_path = f"uploads/{filename}"  # Percorso relativo alla cartella static
                else:
                    flash('Errore durante il salvataggio dell\'immagine ridimensionata.', 'danger')
            except Exception as e:
                flash(f'Errore durante l\'elaborazione dell\'immagine: {e}', 'danger')
                current_app.logger.error(f"Errore in create_post durante il salvataggio immagine: {e}")

        # Gestione URL immagine
        elif form.image_url.data: # Usiamo elif per dare priorità al file caricato se entrambi forniti
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
            upload_path = os.path.join(current_app.root_path, 'static/uploads')
            os.makedirs(upload_path, exist_ok=True)
            # Chiama save_picture per ridimensionare e salvare la nuova immagine
            try:
                filename = save_picture(form.image_file.data, upload_path, form.image_file.data.filename)
                if filename:
                    # Qui potresti voler eliminare la vecchia immagine se presente e diversa
                    # if post.image_path and os.path.exists(os.path.join(upload_path, os.path.basename(post.image_path))):
                    #     os.remove(os.path.join(upload_path, os.path.basename(post.image_path)))
                    post.image_path = f"uploads/{filename}"
                    post.image_url = None  # Resetta URL se si carica un file
                else:
                    flash('Errore durante il salvataggio della nuova immagine ridimensionata.', 'danger')
            except Exception as e:
                flash(f'Errore durante l\'elaborazione della nuova immagine: {e}', 'danger')
                current_app.logger.error(f"Errore in edit_post durante il salvataggio immagine: {e}")

        elif form.image_url.data:
            post.image_url = form.image_url.data
            # Qui potresti voler eliminare la vecchia immagine fisica se si passa a un URL
            # if post.image_path and os.path.exists(os.path.join(current_app.root_path, 'static', post.image_path)):
            #    os.remove(os.path.join(current_app.root_path, 'static', post.image_path))
            post.image_path = None  # Resetta file se si inserisce un URL
        
        db.session.commit()
        flash('Il tuo post è stato aggiornato!', 'success')
        return redirect(url_for('posts.view_post', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
        # Non pre-popolare il campo file, ma l'URL sì
        form.image_url.data = post.image_url 
        # Se vuoi mostrare il nome del file corrente (non il file stesso), dovresti passare post.image_path al template
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


def save_picture(form_picture_data, output_folder, filename_base):
    """Salva l'immagine caricata dopo averla ridimensionata."""
    filename = secure_filename(filename_base)
    picture_path = os.path.join(output_folder, filename)

    # Dimensione desiderata (es. altezza massima 600px)
    output_size = (None, 600) # None per la larghezza la farà calcolare mantenendo le proporzioni

    try:
        img = Image.open(form_picture_data)
        
        # Mantenere le proporzioni basate sull'altezza
        if output_size[1] is not None:
            h_percent = (output_size[1] / float(img.size[1]))
            w_size = int((float(img.size[0]) * float(h_percent)))
            final_size = (w_size, output_size[1])
        elif output_size[0] is not None: # Se invece si volesse basare sulla larghezza
            w_percent = (output_size[0] / float(img.size[0]))
            h_size = int((float(img.size[1]) * float(w_percent)))
            final_size = (output_size[0], h_size)
        else: # Se non specificata altezza o larghezza, usa originale (o imposta un default)
            final_size = img.size

        img.thumbnail(final_size) # .thumbnail modifica l'immagine in-place e mantiene le proporzioni
        img.save(picture_path)
    except Exception as e:
        current_app.logger.error(f"Errore nel salvataggio/ridimensionamento immagine: {e}")
        # Potresti voler sollevare l'eccezione o ritornare un errore
        # Per ora, salviamo l'originale se il ridimensionamento fallisce
        try:
            form_picture_data.seek(0) # Riporta il puntatore del file all'inizio se è stato letto
            form_picture_data.save(picture_path)
        except Exception as e_save:
             current_app.logger.error(f"Errore nel salvataggio immagine originale dopo fallimento resize: {e_save}")
             return None # O gestire l'errore diversamente

    return filename