from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from app import db
from app.models.user import User
import os

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip()
        password = data.get('password', '')
        remember = bool(data.get('remember', False))

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password) and user.is_active:
            login_user(user, remember=remember)
            user.last_seen = db.func.now()
            db.session.commit()

            if request.is_json:
                return {'success': True, 'redirect': url_for('main.index')}

            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        if request.is_json:
            return {'success': False, 'message': 'Invalid email or password'}, 401
        flash('Invalid email or password', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')

        errors = []
        if not username or len(username) < 3:
            errors.append('Username must be at least 3 characters')
        if not email or '@' not in email:
            errors.append('Valid email required')
        if not password or len(password) < 6:
            errors.append('Password must be at least 6 characters')
        if User.query.filter_by(username=username).first():
            errors.append('Username already taken')
        if User.query.filter_by(email=email).first():
            errors.append('Email already registered')

        if errors:
            if request.is_json:
                return {'success': False, 'message': errors[0]}, 400
            for e in errors:
                flash(e, 'error')
            return render_template('auth/register.html')

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password)
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)

        if request.is_json:
            return {'success': True, 'redirect': url_for('main.index')}
        return redirect(url_for('main.index'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        data = request.form
        current_user.username = data.get('username', current_user.username).strip()
        current_user.bio = data.get('bio', current_user.bio).strip()
        current_user.theme = data.get('theme', current_user.theme)

        if 'avatar' in request.files:
            file = request.files['avatar']
            if file and file.filename:
                from app.utils.helpers import allowed_image, save_file
                if allowed_image(file.filename):
                    from flask import current_app
                    filename = save_file(file, current_app.config['AVATARS_FOLDER'])
                    if filename:
                        current_user.avatar = filename

        if data.get('new_password'):
            if current_user.check_password(data.get('current_password', '')):
                current_user.set_password(data['new_password'])
            else:
                flash('Current password incorrect', 'error')
                return redirect(url_for('auth.profile'))

        db.session.commit()
        flash('Profile updated!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('auth/profile.html')
