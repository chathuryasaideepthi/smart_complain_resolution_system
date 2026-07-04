from datetime import datetime
from database import db

class AIPrediction(db.Model):
    __tablename__ = 'ai_predictions'

    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaints.id'), nullable=False)
    classification = db.Column(db.String(120), nullable=True)
    duplicate_score = db.Column(db.Float, nullable=True)
    priority = db.Column(db.String(32), nullable=True)
    sentiment = db.Column(db.String(32), nullable=True)
    summary = db.Column(db.Text, nullable=True)
    resolution_eta = db.Column(db.String(64), nullable=True)
    spam_score = db.Column(db.Float, nullable=True)
    verified_image = db.Column(db.Boolean, default=False)
    extracted_text = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    complaint = db.relationship('Complaint', backref='ai_prediction')

    def __repr__(self):
        return f'<AIPrediction {self.complaint_id}>'
