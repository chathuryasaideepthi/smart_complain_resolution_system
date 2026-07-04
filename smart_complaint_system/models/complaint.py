from datetime import datetime
from database import db

class Complaint(db.Model):
    __tablename__ = 'complaints'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    citizen_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    officer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    priority = db.Column(db.String(32), nullable=False, default='Medium')
    status = db.Column(db.String(32), nullable=False, default='Submitted')
    is_anonymous = db.Column(db.Boolean, default=False)
    attachment_image = db.Column(db.String(255), nullable=True)
    attachment_video = db.Column(db.String(255), nullable=True)
    attachment_document = db.Column(db.String(255), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    sentiment = db.Column(db.String(32), nullable=True)
    department_prediction = db.Column(db.String(120), nullable=True)
    priority_prediction = db.Column(db.String(32), nullable=True)
    resolution_eta = db.Column(db.String(64), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    citizen = db.relationship('User', back_populates='complaints', foreign_keys=[citizen_id])
    officer = db.relationship('User', back_populates='assigned_complaints', foreign_keys=[officer_id])
    department = db.relationship('Department', back_populates='complaints')
    history = db.relationship('ComplaintStatusHistory', back_populates='complaint', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='complaint', cascade='all, delete-orphan')
    assignments = db.relationship('Assignment', back_populates='complaint', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Complaint {self.id} {self.title}>'
