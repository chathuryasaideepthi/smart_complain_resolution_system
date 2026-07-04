from datetime import datetime
from database import db

class ComplaintStatusHistory(db.Model):
    __tablename__ = 'complaint_status_history'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    remarks = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship('Complaint', back_populates='history')

    def __repr__(self):
        return f'<ComplaintStatusHistory {self.complaint_id} {self.status}>'
