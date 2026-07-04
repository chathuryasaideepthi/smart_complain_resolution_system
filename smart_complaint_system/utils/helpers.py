import os
from datetime import datetime
from flask import current_app
from werkzeug.utils import secure_filename

ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'xlsx'}


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def save_uploaded_file(file_storage, subfolder):
    if not file_storage:
        return None
    filename = secure_filename(file_storage.filename)
    if filename == '':
        return None
    upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_folder, exist_ok=True)
    filepath = os.path.join(upload_folder, filename)
    file_storage.save(filepath)
    return os.path.join(subfolder, filename)


def format_datetime(value):
    if not value:
        return ''
    return value.strftime('%Y-%m-%d %H:%M')


def round_value(value):
    try:
        return round(value, 2)
    except Exception:
        return value
