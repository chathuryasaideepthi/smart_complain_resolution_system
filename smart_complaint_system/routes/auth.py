from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from database import db
from smart_complaint_system.models.user import User
from smart_complaint_system.models.role import Role
from smart_complaint_system.models.department import Department

auth_bp = Blueprint('auth', __name__)

def get_dashboard_redirect():
    role = current_user.role.name if current_user.is_authenticated and current_user.role else None
    if role == 'Admin':
        return url_for('admin.admin_dashboard')
    if role == 'Officer':
        return url_for('officer.officer_dashboard')
    if role == 'Department Head':
        return url_for('department.department_dashboard')
    return url_for('dashboard.dashboard')

@auth_bp.route('/')
def home():
    if current_user.is_authenticated:
        return redirect(get_dashboard_redirect())
    return redirect(url_for('auth.login'))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(get_dashboard_redirect())
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = request.form.get('remember') == 'on'
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash('Welcome back!', 'success')
            return redirect(get_dashboard_redirect())
        flash('Invalid email or password', 'danger')
    return render_template('login.html')

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    departments = Department.query.all()
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department_id = request.form.get('department_id')
        if User.query.filter_by(email=email).first():
            flash('Email already exists', 'warning')
        else:
            role = Role.query.filter_by(name='Citizen').first()
            user = User(name=name, email=email, department_id=department_id, role=role)
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('Registration complete. Please login.', 'success')
            return redirect(url_for('auth.login'))
    return render_template('register.html', departments=departments)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logout successful.', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        if user:
            flash('A reset link has been sent to your email.', 'success')
        else:
            flash('Email not found.', 'warning')
    return render_template('forgot_password.html')
