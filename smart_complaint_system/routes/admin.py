from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from smart_complaint_system.models.user import User
from smart_complaint_system.models.department import Department
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.role import Role
from database import db

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required():
    if not current_user.is_authenticated or current_user.role.name != 'Admin':
        return False
    return True

@admin_bp.route('/', methods=['GET', 'POST'])
@login_required
def admin_dashboard():
    if not admin_required():
        return render_template('unauthorized.html'), 403

    if request.method == 'POST':
        form_type = request.form.get('form_type')
        if form_type == 'department':
            name = request.form.get('name')
            description = request.form.get('description')
            if not name:
                flash('Department name is required.', 'warning')
                return redirect(url_for('admin.admin_dashboard'))
            if Department.query.filter_by(name=name).first():
                flash('Department already exists.', 'warning')
                return redirect(url_for('admin.admin_dashboard'))
            department = Department(name=name, description=description)
            db.session.add(department)
            db.session.commit()
            flash('Department added successfully.', 'success')
            return redirect(url_for('admin.admin_dashboard') + '#departments')
        if form_type == 'user':
            full_name = request.form.get('full_name')
            email = request.form.get('email')
            password = request.form.get('password')
            role_id = request.form.get('role_id')
            department_id = request.form.get('department_id')
            if not all([full_name, email, password, role_id]):
                flash('All user fields are required.', 'warning')
                return redirect(url_for('admin.admin_dashboard') + '#officers')
            if User.query.filter_by(email=email).first():
                flash('Email already exists.', 'warning')
                return redirect(url_for('admin.admin_dashboard') + '#officers')
            role = Role.query.get(int(role_id))
            department = Department.query.get(int(department_id)) if department_id else None
            user = User(name=full_name, email=email, role=role, department_id=department.id if department else None)
            user.password = password
            db.session.add(user)
            db.session.commit()
            flash('User account created successfully.', 'success')
            return redirect(url_for('admin.admin_dashboard') + '#officers')

    total_users = User.query.count()
    total_officers = User.query.filter(User.role.has(name='Officer')).count()
    total_departments = Department.query.count()
    total_complaints = Complaint.query.count()
    pending = Complaint.query.filter(Complaint.status.in_(['Submitted', 'Verified', 'Assigned', 'In Progress'])).count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    departments = Department.query.order_by(Department.name).all()
    users = User.query.order_by(User.name).all()
    roles = Role.query.order_by(Role.name).all()
    officers = User.query.filter(User.role.has(name='Officer')).all()
    officer_stats = []
    for officer in officers:
        total_assigned = Complaint.query.filter_by(officer_id=officer.id).count()
        total_completed = Complaint.query.filter_by(officer_id=officer.id).filter(Complaint.status.in_(['Resolved', 'Closed'])).count()
        total_pending_officer = Complaint.query.filter_by(officer_id=officer.id).filter(Complaint.status.in_(['Assigned', 'In Progress'])).count()
        officer_stats.append({
            'officer': officer,
            'assigned': total_assigned,
            'completed': total_completed,
            'pending': total_pending_officer,
        })
    return render_template('admin_dashboard.html', total_users=total_users, total_officers=total_officers,
                           total_departments=total_departments, total_complaints=total_complaints,
                           pending=pending, resolved=resolved, departments=departments,
                           users=users, roles=roles, officer_stats=officer_stats)

@admin_bp.route('/departments/delete/<int:department_id>', methods=['POST'])
@login_required
def delete_department(department_id):
    if not admin_required():
        return render_template('unauthorized.html'), 403
    department = Department.query.get_or_404(department_id)
    if department.users or department.complaints:
        flash('Cannot delete a department that has users or complaints.', 'danger')
        return redirect(url_for('admin.admin_dashboard'))
    db.session.delete(department)
    db.session.commit()
    flash('Department deleted successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#departments')

@admin_bp.route('/users/delete/<int:user_id>', methods=['POST'])
@login_required
def delete_user(user_id):
    if not admin_required():
        return render_template('unauthorized.html'), 403
    user = User.query.get_or_404(user_id)
    if user.role.name == 'Admin':
        flash('Cannot delete an admin user.', 'danger')
        return redirect(url_for('admin.admin_dashboard') + '#officers')
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully.', 'success')
    return redirect(url_for('admin.admin_dashboard') + '#officers')
