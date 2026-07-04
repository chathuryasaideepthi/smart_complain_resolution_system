# Smart Complaint Resolution System

A complete Flask-based complaint management platform with AI-enabled complaint classification, priority prediction, duplicate detection, and reporting.

## Features
- Role-based authentication: Citizen, Officer, Department Head, Admin
- Complaint submission with evidence uploads
- AI classification, summary, sentiment analysis, and spam detection
- Chat between citizen and officer
- Timeline tracking and notifications
- Reports in CSV, Excel, and PDF
- Modern Bootstrap 5 dashboard UI

## Folder Structure
- `app.py` - main Flask application
- `config.py` - application configuration
- `database.py` - SQLAlchemy instance
- `smart_complaint_system/` - app package
  - `models/` - SQLAlchemy models
  - `routes/` - Flask blueprints
  - `services/` - AI and business services
  - `utils/` - helper utilities
  - `templates/` - HTML Jinja templates
  - `static/` - CSS, JS, images, uploads
- `requirements.txt` - Python dependencies
- `seed_data.py` - initial sample data

## Setup Instructions
1. Install Python 3.11 or higher.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a MySQL database and update `DATABASE_URI` in `config.py` or create a `.env` file with:
   ```env
   DATABASE_URI=mysql+mysqlconnector://root:password@localhost/smart_complaint_db
   SECRET_KEY=change-me
   MAIL_USERNAME=you@example.com
   MAIL_PASSWORD=your-mail-password
   ```
5. Run database migrations and seed data:
   ```bash
   python seed_data.py
   ```
6. Start the application:
   ```bash
   python app.py
   ```
7. Open `http://127.0.0.1:5000` in the browser.

## Default Accounts
- Admin: `admin@example.com` / `Admin@123`
- Officer: `officer@example.com` / `Officer@123`
- Department Head: `head@example.com` / `Head@123`
- Citizen: `citizen@example.com` / `Citizen@123`

## Notes
- Make sure Tesseract OCR is installed if using image text extraction.
- The application is configured for local development with debug mode enabled.
