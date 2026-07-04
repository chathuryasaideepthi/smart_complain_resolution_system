import random
import string
from app import app
from database import db
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.department import Department
from smart_complaint_system.models.user import User


def random_suffix(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))


def login(client, email, password):
    response = client.post('/login', data={'email': email, 'password': password}, follow_redirects=True)
    assert response.status_code == 200, f'Login failed for {email}'
    page = response.data.decode('utf-8')
    assert 'Logout' in page or 'Profile' in page, f'Unexpected login page content for {email}'
    print(f'[OK] Logged in as {email}')


def logout(client):
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    print('[OK] Logged out')


def create_complaint(client, department_id):
    suffix = random_suffix()
    title = f'Test complaint {suffix}'
    description = f'This is a test complaint created for automated workflow validation {suffix}.'
    data = {
        'title': title,
        'description': description,
        'department_id': str(department_id),
        'location': 'Test City',
        'priority': 'High',
    }
    response = client.post('/complaints/new', data=data, follow_redirects=True)
    assert response.status_code == 200, 'Complaint submission failed'
    assert 'Complaint submitted successfully' in response.data.decode('utf-8'), 'Complaint submission did not succeed'
    complaint = Complaint.query.filter_by(title=title).first()
    assert complaint is not None, 'Complaint was not saved to the database'
    print(f'[OK] Complaint created: id={complaint.id}')
    return complaint


def assign_complaint(client, complaint_id, officer_id):
    response = client.post(f'/department/assign/{complaint_id}', data={'officer_id': str(officer_id)}, follow_redirects=True)
    assert response.status_code == 200, 'Assignment request failed'
    updated = Complaint.query.get(complaint_id)
    assert updated.officer_id == officer_id, 'Complaint officer assignment failed'
    assert updated.status == 'Assigned', f'Complaint status expected Assigned, got {updated.status}'
    print(f'[OK] Complaint assigned to officer_id={officer_id}')


def officer_complete(client, complaint_id):
    response = client.post(f'/officer/complete/{complaint_id}', follow_redirects=True)
    assert response.status_code == 200, 'Officer complete request failed'
    updated = Complaint.query.get(complaint_id)
    assert updated.status == 'Resolved', f'Complaint status expected Resolved, got {updated.status}'
    print(f'[OK] Complaint marked Resolved by officer')


with app.app_context():
    department = Department.query.first()
    assert department is not None, 'No department found in the database'
    head_user = User.query.filter_by(email='head@example.com').first()
    assert head_user is not None, 'Department head user not found'
    officer_user = User.query.filter_by(email='officer@example.com').first()
    assert officer_user is not None, 'Officer user not found'

    with app.test_client() as client:
        login(client, 'citizen@example.com', 'Citizen@123')
        complaint = create_complaint(client, department.id)
        logout(client)

        login(client, 'head@example.com', 'Head@123')
        assign_complaint(client, complaint.id, officer_user.id)
        logout(client)

        login(client, 'officer@example.com', 'Officer@123')
        response = client.get('/officer/')
        assert response.status_code == 200
        assert str(complaint.id) in response.data.decode('utf-8'), 'Officer dashboard does not show assigned complaint'
        officer_complete(client, complaint.id)
        logout(client)

        login(client, 'citizen@example.com', 'Citizen@123')
        response = client.get('/complaints/my')
        page = response.data.decode('utf-8')
        assert 'Resolved' in page, 'Citizen complaint status update not visible'
        print('[OK] Citizen sees the resolved complaint status')

print('\nWorkflow test completed successfully.')
