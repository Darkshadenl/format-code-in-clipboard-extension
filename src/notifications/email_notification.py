from pydantic_settings import BaseSettings
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class EmailSettings(BaseSettings):
    SMTP_SERVER: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    EMAIL_USER: str
    EMAIL_PASSWORD: str

    class Config:
        env_file = ".env"


def send_notification_email(to_email: str, subject: str, content: str) -> None:
    settings = EmailSettings()

    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = settings.EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.EMAIL_USER, settings.EMAIL_PASSWORD)
        server.send_message(msg)


if __name__ == "__main__":
    # Example usage
    to_email = "gi1fd8wmvs@pomail.net"  # Replace with your email
    subject = "Zagwijnstraat 30 is beschikbaar! Test"
    content = "This is a test email from the notification system!"

    try:
        send_notification_email(to_email, subject, content)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
