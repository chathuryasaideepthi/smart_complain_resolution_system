from datetime import datetime
from database import db

class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    attachment = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender = db.relationship('User', back_populates='messages')
    complaint = db.relationship('Complaint', backref='messages')

    def __repr__(self):
        return f'<Message {self.id}>'
