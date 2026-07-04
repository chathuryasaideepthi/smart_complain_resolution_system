from flask import Blueprint, render_template, request, send_file
from flask_login import login_required
from database import db
from smart_complaint_system.models.complaint import Complaint
from smart_complaint_system.models.department import Department
from smart_complaint_system.models.user import User
import pandas as pd
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

reports_bp = Blueprint('reports', __name__, url_prefix='/reports')

@reports_bp.route('/')
@login_required
def reports():
    return render_template('reports.html')

@reports_bp.route('/export/csv')
@login_required
def export_csv():
    complaints = Complaint.query.all()
    data = [
        {
            'ID': c.id,
            'Title': c.title,
            'Status': c.status,
            'Priority': c.priority,
            'Department': c.department.name if c.department else '',
            'Created At': c.created_at,
        }
        for c in complaints
    ]
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='complaints.csv', mimetype='text/csv')

@reports_bp.route('/export/excel')
@login_required
def export_excel():
    complaints = Complaint.query.all()
    data = [
        {
            'ID': c.id,
            'Title': c.title,
            'Status': c.status,
            'Priority': c.priority,
            'Department': c.department.name if c.department else '',
            'Created At': c.created_at,
        }
        for c in complaints
    ]
    df = pd.DataFrame(data)
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='complaints.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

@reports_bp.route('/export/pdf')
@login_required
def export_pdf():
    complaints = Complaint.query.limit(20).all()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.setTitle('Complaint Report')
    y = 700
    pdf.drawString(50, 750, 'Complaint Report')
    for complaint in complaints:
        pdf.drawString(50, y, f'{complaint.id}: {complaint.title} [{complaint.status}]')
        y -= 20
        if y < 50:
            pdf.showPage()
            y = 750
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='complaints.pdf', mimetype='application/pdf')
