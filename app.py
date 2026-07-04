from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from config import Config
from database import db
from smart_complaint_system.models.user import User
from smart_complaint_system.routes.auth import auth_bp
from smart_complaint_system.routes.dashboard import dashboard_bp
from smart_complaint_system.routes.complaints import complaints_bp
from smart_complaint_system.routes.reports import reports_bp
from smart_complaint_system.routes.chat import chat_bp
from smart_complaint_system.routes.admin import admin_bp
from smart_complaint_system.routes.officer import officer_bp
from smart_complaint_system.routes.department import department_bp

app = Flask(
    __name__,
    instance_relative_config=True,
    template_folder='smart_complaint_system/templates',
    static_folder='smart_complaint_system/static',
)
app.config.from_object(Config)
app.config.from_pyfile('config.py', silent=True)

# extensions
db.init_app(app)
migrate = Migrate(app, db)
login_manager = LoginManager(app)
mail = Mail(app)

login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# register blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(complaints_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(chat_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(officer_bp)
app.register_blueprint(department_bp)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
