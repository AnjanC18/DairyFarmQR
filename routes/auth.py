from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        remember = bool(request.form.get('remember'))

        user = User.query.filter((User.username == username) | (User.email == username)).first()

        if user and user.check_password(password):
            if not user.is_active:
                flash('Your account has been deactivated. Please contact farm administrator.', 'danger')
                return render_template('login.html')

            login_user(user, remember=remember)
            flash(f'Welcome back, {user.full_name}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page if next_page and next_page.startswith('/') else url_for('main.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))

    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        role = request.form.get('role', 'manager')
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not username or not email or not password:
            flash('All required fields must be filled.', 'danger')
            return render_template('register.html')

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html')

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html')

        # Check username uniqueness
        if User.query.filter_by(username=username).first():
            flash(f'Username "{username}" is already taken.', 'danger')
            return render_template('register.html')

        # Check email uniqueness
        if User.query.filter_by(email=email).first():
            flash(f'Email "{email}" is already registered.', 'danger')
            return render_template('register.html')

        # Create user
        new_user = User(
            full_name=full_name,
            username=username,
            email=email,
            role=role if role in ('admin', 'manager', 'staff') else 'manager'
        )
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash(f'Account created successfully! Welcome to Smart Dairy Farm, {new_user.full_name}.', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('register.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        if not full_name or not email:
            flash('Full Name and Email are required.', 'danger')
            return render_template('profile.html', user=current_user)

        # Check email uniqueness if changed
        existing_email = User.query.filter(User.email == email, User.id != current_user.id).first()
        if existing_email:
            flash('Email already registered by another account.', 'danger')
            return render_template('profile.html', user=current_user)

        current_user.full_name = full_name
        current_user.email = email

        if new_password:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters long.', 'danger')
                return render_template('profile.html', user=current_user)
            if new_password != confirm_password:
                flash('New password and confirmation do not match.', 'danger')
                return render_template('profile.html', user=current_user)
            current_user.set_password(new_password)

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('auth.profile'))

    return render_template('profile.html', user=current_user)
