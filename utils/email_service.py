import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# Internal helper to send emails
def _send_email(to_email, subject, html_message):
    sender_email = os.getenv("EMAIL_HOST_USER")
    sender_password = os.getenv("EMAIL_HOST_PASSWORD")
    smtp_host = os.getenv("EMAIL_HOST")
    smtp_port = int(os.getenv("EMAIL_PORT", 587))  # Default to 587 if not set

    if not all([sender_email, sender_password, smtp_host, smtp_port]):
        print("❌ Missing email configuration in .env")
        return False

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = to_email
    message.attach(MIMEText(html_message, "html"))

    try:
        server = smtplib.SMTP(smtp_host, smtp_port)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())
        server.quit()
        print(f"✅ Email sent to {to_email}")
        return True
    except Exception as e:
        print("❌ Email sending failed:", e)
        return False


# Public method: Send OTP email
def send_otp_email(to_email, otp):
    html_content = f"""
    <html>
        <body>
            <p>Hello,<br>
            Your OTP for password reset is: <b>{otp}</b><br>
            It will expire in 10 minutes.
            </p>
        </body>
    </html>
    """
    return _send_email(to_email, "LMS Password Reset OTP", html_content)


# Public method: Send any HTML email
def send_email(to_email, subject, html_message):
    return _send_email(to_email, subject, html_message)