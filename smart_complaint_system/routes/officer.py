from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from database import db
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.complaint_status import ComplaintStatusHistory
from smart_complaint_system.models.notification import Notification

officer_bp = Blueprint('officer', __name__, url_prefix='/officer')

@officer_bp.route('/')
@login_required
def officer_dashboard():
    if current_user.role.name != 'Officer':
        return render_template('unauthorized.html'), 403
    assigned = Complaint.query.filter_by(officer_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    pending = [c for c in assigned if c.status not in ['Resolved', 'Closed', 'Rejected']]
    completed = [c for c in assigned if c.status in ['Resolved', 'Closed']]
    return render_template('officer_dashboard.html', assigned=assigned, pending=pending, completed=completed)

@officer_bp.route('/update-status/<int:complaint_id>', methods=['POST'])
@login_required
def update_status(complaint_id):
    if current_user.role.name != 'Officer':
        return render_template('unauthorized.html'), 403
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.officer_id != current_user.id:
        flash('You may only update your assigned complaints.', 'warning')
        return redirect(url_for('officer.officer_dashboard'))
    status = request.form.get('status')
    remarks = request.form.get('remarks')
    if status:
        complaint.status = status
        history = ComplaintStatusHistory(complaint_id=complaint.id, status=status, remarks=remarks)
        db.session.add(history)
        db.session.commit()
        notification = Notification(user_id=complaint.citizen_id, complaint_id=complaint.id,
                                    title='Complaint Status Updated', message=f'Your complaint status changed to {status}.')
        db.session.add(notification)
        db.session.commit()
        flash('Status updated.', 'success')
    return redirect(url_for('officer.officer_dashboard'))

@officer_bp.route('/complete/<int:complaint_id>', methods=['POST'])
@login_required
def complete_issue(complaint_id):
    if current_user.role.name != 'Officer':
        return render_template('unauthorized.html'), 403
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.officer_id != current_user.id:
        flash('You may only complete your assigned complaints.', 'warning')
        return redirect(url_for('officer.officer_dashboard'))
    complaint.status = 'Resolved'
    history = ComplaintStatusHistory(complaint_id=complaint.id, status='Resolved', remarks='Marked complete by officer')
    db.session.add(history)
    db.session.commit()
    notification = Notification(user_id=complaint.citizen_id, complaint_id=complaint.id,
                                title='Complaint Completed', message=f'Your complaint {complaint.title} has been completed.')
    db.session.add(notification)
    db.session.commit()
    flash('Complaint marked as completed.', 'success')
    return redirect(url_for('officer.officer_dashboard'))

@officer_bp.route('/reopen/<int:complaint_id>', methods=['POST'])
@login_required
def reopen_issue(complaint_id):
    if current_user.role.name != 'Officer':
        return render_template('unauthorized.html'), 403
    complaint = Complaint.query.get_or_404(complaint_id)
    if complaint.officer_id != current_user.id:
        flash('You may only update your assigned complaints.', 'warning')
        return redirect(url_for('officer.officer_dashboard'))
    complaint.status = 'In Progress'
    history = ComplaintStatusHistory(complaint_id=complaint.id, status='In Progress', remarks='Marked in progress by officer')
    db.session.add(history)
    db.session.commit()
    notification = Notification(user_id=complaint.citizen_id, complaint_id=complaint.id,
                                title='Complaint Reopened', message=f'Your complaint {complaint.title} is back in progress.')
    db.session.add(notification)
    db.session.commit()
    flash('Complaint marked as in progress.', 'success')
    return redirect(url_for('officer.officer_dashboard'))
