from datetime import datetime
from database import db

class Assignment(db.Model):
    __tablename__ = 'assignments'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(64), nullable=False, default='Assigned')

    complaint = db.relationship('Complaint', back_populates='assignments')
    officer = db.relationship('User', back_populates='assignments')

    def __repr__(self):
        return f'<Assignment {self.id}>'
