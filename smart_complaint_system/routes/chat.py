from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required, current_user
from database import db
from smart_complaint_system.models.message import Message
from smart_complaint_system.models.complaint import Complaint

chat_bp = Blueprint('chat', __name__, url_prefix='/chat')

@chat_bp.route('/<int:complaint_id>')
@login_required
def chat_room(complaint_id):
    complaint = Complaint.query.get_or_404(complaint_id)
    messages = Message.query.filter_by(complaint_id=complaint_id).order_by(Message.created_at.asc()).all()
    return render_template('chat.html', complaint=complaint, messages=messages)

@chat_bp.route('/send', methods=['POST'])
@login_required
def send_message():
    complaint_id = request.form.get('complaint_id')
    content = request.form.get('content')
    if not content:
        return jsonify({'success': False, 'message': 'Message cannot be empty'})
    message = Message(sender_id=current_user.id, complaint_id=complaint_id, content=content)
    db.session.add(message)
    db.session.commit()
    return jsonify({'success': True, 'message': 'Message sent'})
