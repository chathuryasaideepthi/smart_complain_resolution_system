from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from database import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    phone = db.Column(db.String(30), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    role = db.relationship('Role', back_populates='users')
    department = db.relationship('Department', back_populates='users')
    complaints = db.relationship('Complaint', back_populates='citizen', foreign_keys='Complaint.citizen_id')
    assigned_complaints = db.relationship('Complaint', back_populates='officer', foreign_keys='Complaint.officer_id')
    notifications = db.relationship('Notification', back_populates='user')
    messages = db.relationship('Message', back_populates='sender', foreign_keys='Message.sender_id')
    feedback = db.relationship('Feedback', back_populates='user')
    assignments = db.relationship('Assignment', back_populates='officer')

    @property
    def password(self):
        raise AttributeError('Password is not readable.')

    @password.setter
    def password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)

    def has_role(self, role_name):
        return self.role and self.role.name == role_name

    def __repr__(self):
        return f'<User {self.email}>'
