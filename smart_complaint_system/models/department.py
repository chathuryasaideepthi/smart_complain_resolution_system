from database import db

class Department(db.Model):
    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=True)

    users = db.relationship('User', back_populates='department')
    complaints = db.relationship('Complaint', back_populates='department')

    def __repr__(self):
        return f'<Department {self.name}>'
