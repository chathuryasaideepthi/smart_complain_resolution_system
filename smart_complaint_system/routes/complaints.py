import os
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from database import db
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.department import Department
from smart_complaint_system.models.complaint_status import ComplaintStatusHistory
from smart_complaint_system.models.notification import Notification
from smart_complaint_system.services.ai_service import classify_department, predict_priority, analyze_sentiment, summarize_text, estimate_resolution_time, find_duplicate, detect_spam, verify_image_relevance
from smart_complaint_system.utils.helpers import save_uploaded_file

complaints_bp = Blueprint('complaints', __name__, url_prefix='/complaints')

@complaints_bp.route('/new', methods=['GET', 'POST'])
@login_required
def create_complaint():
    departments = Department.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        department_id = request.form.get('department_id')
        location = request.form.get('location')
        latitude = request.form.get('latitude') or None
        longitude = request.form.get('longitude') or None
        priority = request.form.get('priority')
        anonymous = request.form.get('anonymous') == 'on'
        image = request.files.get('image')
        video = request.files.get('video')
        document = request.files.get('document')

        try:
            department_id = int(department_id) if department_id else None
        except (TypeError, ValueError):
            department_id = None

        if not title or not description or not department_id or not priority:
            flash('Please fill in all required fields and select a department.', 'warning')
            return render_template('complaint_form.html', departments=departments)

        department = Department.query.get(department_id)
        if not department:
            flash('Selected department is invalid. Please choose a valid department.', 'warning')
            return render_template('complaint_form.html', departments=departments)

        if not location and latitude and longitude:
            location = f'Lat: {latitude}, Lon: {longitude}'

        existing_complaints = Complaint.query.filter(Complaint.id != None).all()
        duplicate_complaint, duplicate_score = find_duplicate(description, existing_complaints)
        if duplicate_score > 0.75:
            flash('Similar complaint already exists.', 'warning')
            return redirect(url_for('complaints.create_complaint'))

        department_prediction = classify_department(description)
        priority_prediction = predict_priority(description)
        sentiment = analyze_sentiment(description)
        summary = summarize_text(description)
        resolution_eta = estimate_resolution_time(priority_prediction)
        spam_detected = detect_spam(description)

        if spam_detected:
            flash('Complaint content looks suspicious', 'danger')
            return redirect(url_for('complaints.create_complaint'))

        path_image = save_uploaded_file(image, 'images') if image else None
        path_video = save_uploaded_file(video, 'videos') if video else None
        path_document = save_uploaded_file(document, 'documents') if document else None
        complaint = Complaint(
            title=title,
            description=description,
            citizen_id=current_user.id,
            department_id=department_id,
            location=location,
            latitude=float(latitude) if latitude else None,
            longitude=float(longitude) if longitude else None,
            priority=priority,
            is_anonymous=anonymous,
            attachment_image=path_image,
            attachment_video=path_video,
            attachment_document=path_document,
            summary=summary,
            sentiment=sentiment,
            department_prediction=department_prediction,
            priority_prediction=priority_prediction,
            resolution_eta=resolution_eta,
        )
        db.session.add(complaint)
        db.session.commit()

        history = ComplaintStatusHistory(complaint_id=complaint.id, status='Submitted', remarks='Complaint submitted by citizen')
        db.session.add(history)
        db.session.commit()

        notification = Notification(user_id=current_user.id, complaint_id=complaint.id,
                                    title='Complaint Submitted', message='Your complaint has been submitted successfully.')
        db.session.add(notification)
        db.session.commit()

        flash('Complaint submitted successfully.', 'success')
        return redirect(url_for('complaints.my_complaints'))
    return render_template('complaint_form.html', departments=departments)

@complaints_bp.route('/my')
@login_required
def my_complaints():
    complaints = Complaint.query.filter_by(citizen_id=current_user.id).order_by(Complaint.created_at.desc()).all()
    return render_template('my_complaints.html', complaints=complaints)

@complaints_bp.route('/<int:complaint_id>')
@login_required
def complaint_detail(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    return render_template('complaint_detail.html', complaint=complaint)

@complaints_bp.route('/track/<int:complaint_id>')
@login_required
def track_complaint(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    timeline = complaint.history
    return render_template('track_complaint.html', complaint=complaint, timeline=timeline)

@complaints_bp.route('/verify-image', methods=['POST'])
def verify_image():
    data = request.get_json() or {}
    text = data.get('description', '')
    image_path = data.get('image_path', '')
    full_path = os.path.join(current_app.config['UPLOAD_FOLDER'], image_path)
    result = verify_image_relevance(text, full_path)
    return jsonify({'relevant': result})
