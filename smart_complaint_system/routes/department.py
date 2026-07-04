from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from database import db
from smart_complaint_system.models.user import User
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.assignment import Assignment
from smart_complaint_system.models.notification import Notification

department_bp = Blueprint('department', __name__, url_prefix='/department')

@department_bp.route('/')
@login_required
def department_dashboard():
    if current_user.role.name != 'Department Head':
        return render_template('unauthorized.html'), 403

    officers = User.query.filter(User.role.has(name='Officer')).all()
    department_complaints = Complaint.query.filter_by(department_id=current_user.department_id).order_by(Complaint.created_at.desc()).all() if current_user.department_id else Complaint.query.order_by(Complaint.created_at.desc()).all()

    officer_workloads = []
    for officer in officers:
        assigned_count = Complaint.query.filter_by(officer_id=officer.id).filter(~Complaint.status.in_(['Resolved', 'Closed', 'Rejected'])).count()
        officer_workloads.append({'officer': officer, 'active': assigned_count})
    officer_workloads.sort(key=lambda item: item['active'])
    return render_template('department_dashboard.html', officers=officers, department_complaints=department_complaints, officer_workloads=officer_workloads)

@department_bp.route('/assign/<int:complaint_id>', methods=['POST'])
@login_required
def assign_officer(complaint_id):
    if current_user.role.name != 'Department Head':
        return render_template('unauthorized.html'), 403
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.department_id != current_user.department_id:
        flash('You can only assign complaints for your department.', 'warning')
        return redirect(url_for('department.department_dashboard'))
    officer_id = request.form.get('officer_id')
    officer = User.query.get(int(officer_id)) if officer_id else None
    if officer and officer.role.name == 'Officer' and officer.department_id == current_user.department_id:
        complaint.officer_id = officer.id
        complaint.status = 'Assigned'
        assignment = Assignment(complaint_id=complaint.id, officer_id=officer.id)
        notification = Notification(user_id=officer.id, complaint_id=complaint.id,
                                    title='New Assignment', message=f'You have been assigned complaint {complaint.title}.')
        db.session.add(assignment)
        db.session.add(notification)
        db.session.commit()
        flash('Officer assigned successfully', 'success')
    else:
        flash('Invalid officer selection', 'danger')
    return redirect(url_for('department.department_dashboard'))

@department_bp.route('/assign-nearest/<int:complaint_id>', methods=['POST'])
@login_required
def assign_nearest_officer(complaint_id):
    if current_user.role.name != 'Department Head':
        return render_template('unauthorized.html'), 403
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.department_id != current_user.department_id:
        flash('You can only assign complaints for your department.', 'warning')
        return redirect(url_for('department.department_dashboard'))
    officers = User.query.filter_by(department_id=current_user.department_id).filter(User.role.has(name='Officer')).all()
    if not officers:
        flash('No officers available in your department.', 'warning')
        return redirect(url_for('department.department_dashboard'))
    workloads = []
    for officer in officers:
        active_count = Complaint.query.filter_by(officer_id=officer.id).filter(~Complaint.status.in_(['Resolved', 'Closed', 'Rejected'])).count()
        workloads.append((active_count, officer))
    _, officer = min(workloads, key=lambda item: item[0])
    complaint.officer_id = officer.id
    complaint.status = 'Assigned'
    assignment = Assignment(complaint_id=complaint.id, officer_id=officer.id)
    notification = Notification(user_id=officer.id, complaint_id=complaint.id,
                                title='Auto Assignment', message=f'You have been automatically assigned complaint {complaint.title}.')
    db.session.add(assignment)
    db.session.add(notification)
    db.session.commit()
    flash(f'Complaint auto-assigned to {officer.name} with the lightest workload.', 'success')
    return redirect(url_for('department.department_dashboard'))
