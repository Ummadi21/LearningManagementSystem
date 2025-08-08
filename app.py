import sys
import os
from flask import Flask
from extensions import db, bcrypt,socketio
from flask_jwt_extended import JWTManager
from flask_apscheduler import APScheduler
from dotenv import load_dotenv
from datetime import datetime
from utils.email_service import send_email

# --------------------------------------------------
# ✅ Load environment variables from .env file
# --------------------------------------------------
load_dotenv()

# --------------------------------------------------
# ✅ Flask Config Class for easy scaling
# --------------------------------------------------
class Config:
    SCHEDULER_API_ENABLED = True
    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

# --------------------------------------------------
# ✅ Initialize Flask app
# --------------------------------------------------
app = Flask(__name__)  # ✅ FIXED: 'name', not '_name'
app.config.from_object(Config)

# --------------------------------------------------
# ✅ Initialize extensions
# --------------------------------------------------
db.init_app(app)
bcrypt.init_app(app)
jwt = JWTManager(app)

# Scheduler & SocketIO setup
scheduler = APScheduler()
scheduler.init_app(app)
scheduler.start()

# --------------------------------------------------
# ✅ Import and register blueprints
# (AFTER app & extensions are fully initialized)
# --------------------------------------------------
from routes.auth import auth_bp  # Do NOT import otp_store here to avoid circular imports
from routes.protected import protected_bp
from routes.profile import profile_bp
from routes.course import course_bp
from routes.module_lesson import ml_bp
from routes.enrollment import enroll_bp
from routes.payment import payment_bp
from routes.quiz import quiz_bp
from routes.revenue import revenue_bp

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(protected_bp, url_prefix='/api/protected')
app.register_blueprint(profile_bp, url_prefix='/api/profile')
app.register_blueprint(course_bp, url_prefix='/api/courses')
app.register_blueprint(ml_bp, url_prefix='/api/content')
app.register_blueprint(enroll_bp, url_prefix='/api/enrollment')
app.register_blueprint(payment_bp, url_prefix='/api/payment')
app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
app.register_blueprint(revenue_bp, url_prefix='/api/revenue')

# --------------------------------------------------
# ✅ Test route to verify server
# --------------------------------------------------
@app.route('/')
def home():
    return 'LMS Backend is running! ✅'

# --------------------------------------------------
# ✅ Scheduled Tasks
# --------------------------------------------------
@scheduler.task('cron', id='daily_notification', hour=9)
def notify_users():
    from models import User
    users = User.query.all()
    for user in users:
        send_email(
            to_email=user.email,
            subject="LMS Daily Update",
            html_message=f"<p>Hello {user.name},<br>Check out the latest courses and updates in your LMS account.</p>"
        )
    print(f"[{datetime.now()}] ✅ Sent daily notifications to {len(users)} users.")

@scheduler.task('interval', id='otp_cleanup', hours=1)
def clean_expired_otps():
    try:
        from routes.auth import otp_store  # ✅ Imported here to avoid circular import at top
        now = datetime.utcnow()
        expired = [email for email, data in otp_store.items() if data['expires_at'] < now]
        for email in expired:
            otp_store.pop(email)
        print(f"[{datetime.now()}] 🧹 Cleaned up {len(expired)} expired OTPs.")
    except Exception as e:
        print(f"❌ OTP cleanup error: {e}")

# --------------------------------------------------
# ✅ Run the app with SocketIO
# --------------------------------------------------
if __name__ == '__main':  # ✅ FIXED: 'main__'
    socketio.run(app, debug=True)