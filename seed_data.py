from app import app, db
from smart_complaint_system.models.role import Role
from smart_complaint_system.models.department import Department
from smart_complaint_system.models.user import User
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.complaint_status import ComplaintStatusHistory
from smart_complaint_system.models.notification import Notification
from smart_complaint_system.models.assignment import Assignment


def seed_database():
    with app.app_context():
        db.create_all()

        if Role.query.first():
            print('Database already seeded.')
            return

        roles = [
            Role(name='Admin', description='Administrator with full access'),
            Role(name='Officer', description='Officer assigned to resolve complaints'),
            Role(name='Department Head', description='Department head for assignments'),
            Role(name='Citizen', description='Citizen who submits complaints')
        ]
        db.session.add_all(roles)

        departments = [
            Department(name='Water', description='Water supply and leakage complaints'),
            Department(name='Electricity', description='Power outage and electric faults'),
            Department(name='Roads', description='Road repairs and potholes'),
            Department(name='Sanitation', description='Waste management and cleaning'),
            Department(name='Security', description='Public safety and policing'),
            Department(name='Health', description='Health services and clinics')
        ]
        db.session.add_all(departments)
        db.session.commit()

        admin = User(name='Admin User', email='admin@example.com', role_id=roles[0].id, department_id=departments[0].id)
        admin.password = 'Admin@123'
        officer = User(name='Officer One', email='officer@example.com', role_id=roles[1].id, department_id=departments[1].id)
        officer.password = 'Officer@123'
        head = User(name='Department Head', email='head@example.com', role_id=roles[2].id, department_id=departments[1].id)
        head.password = 'Head@123'
        citizen = User(name='Citizen User', email='citizen@example.com', role_id=roles[3].id, department_id=departments[0].id)
        citizen.password = 'Citizen@123'

        db.session.add_all([admin, officer, head, citizen])
        db.session.commit()

        complaint = Complaint(
            title='Water pipeline leak near residential block',
            description='There is a continuous water leak on the main pipeline near the residential block. The water is flooding the road and causing damage to street surfaces.',
            citizen_id=citizen.id,
            department_id=departments[0].id,
            location='Sector 12, City Center',
            priority='High',
            status='Submitted',
            sentiment='Neutral',
            summary='Water pipeline leak flooding the road near residential block.',
            department_prediction='Water',
            priority_prediction='High',
            resolution_eta='3-5 days'
        )
        db.session.add(complaint)
        db.session.commit()

        history = ComplaintStatusHistory(complaint_id=complaint.id, status='Submitted', remarks='Initial complaint submitted by citizen')
        db.session.add(history)
        notification = Notification(user_id=citizen.id, complaint_id=complaint.id,
                                    title='Complaint Created', message='Your complaint has been created and will be reviewed.')
        db.session.add(notification)
        db.session.commit()

        assignment = Assignment(complaint_id=complaint.id, officer_id=officer.id)
        db.session.add(assignment)
        db.session.commit()

        print('Database seeded successfully.')


if __name__ == '__main__':
    seed_database()
