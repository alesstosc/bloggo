from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlparse as url_parse # Modifica questa riga
from flask_login import login_user, logout_user, current_user
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm
from app.models import User
from app.extensions import db

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Username o password non validi', 'danger')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        flash('Login effettuato con successo!', 'success')
        return redirect(next_page)
    return render_template('login.html', title='Login', form=form)

@bp.route('/logout')
def logout():
    logout_user()
    flash('Logout effettuato.', 'info')
    return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulazioni, sei un utente registrato!', 'success')
        return redirect(url_for('auth.login'))
    return render_template('register.html', title='Registrati', form=form)