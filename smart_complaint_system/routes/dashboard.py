from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.department import Department
from smart_complaint_system.models.user import User
from smart_complaint_system.models.feedback import Feedback

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.route('/')
@login_required
def dashboard():
    role = current_user.role.name if current_user.role else 'Citizen'
    if role == 'Admin':
        return redirect(url_for('admin.admin_dashboard'))
    if role == 'Officer':
        return redirect(url_for('officer.officer_dashboard'))
    if role == 'Department Head':
        return redirect(url_for('department.department_dashboard'))

    total_users = User.query.count()
    total_officers = User.query.filter(User.role.has(name='Officer')).count()
    total_departments = Department.query.count()
    total_complaints = Complaint.query.count()
    pending = Complaint.query.filter(Complaint.status.in_(['Submitted', 'Verified', 'Assigned', 'In Progress'])).count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    rejected = Complaint.query.filter_by(status='Rejected').count()
    avg_resolution = 'N/A'
    department_counts = Department.query.all()

    chart_labels = [d.name for d in department_counts]
    chart_values = [Complaint.query.filter_by(department_id=d.id).count() for d in department_counts]
    recent_complaints = Complaint.query.order_by(Complaint.created_at.desc()).limit(5).all()
    return render_template('dashboard.html', role=role, total_users=total_users, total_officers=total_officers,
                           total_departments=total_departments, total_complaints=total_complaints, pending=pending,
                           resolved=resolved, rejected=rejected, avg_resolution=avg_resolution,
                           chart_labels=chart_labels, chart_values=chart_values, recent_complaints=recent_complaints)
