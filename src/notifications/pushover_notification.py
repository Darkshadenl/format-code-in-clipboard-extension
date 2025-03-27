from pydantic_settings import BaseSettings
from typing import Optional
import requests


class PushoverSettings(BaseSettings):
    PUSHOVER_TOKEN: str
    PUSHOVER_USER_KEY: str  # Dit is je user key na registratie

    class Config:
        env_file = ".env"


def send_notification(title: str, message: str, priority: int = 0) -> bool:
    """
    Stuur een notificatie via Pushover

    Args:
        title: Titel van de notificatie
        message: Content van het bericht
        priority: -2 tot 2 (-2 is lowest, 2 is emergency)
    """
    settings = PushoverSettings()

    response = requests.post(
        "https://api.pushover.net/1/messages.json",
        data={
            "token": settings.PUSHOVER_TOKEN,
            "user": settings.PUSHOVER_USER_KEY,
            "title": title,
            "message": message,
            "priority": priority,
        },
    )
    return response.status_code == 200


if __name__ == "__main__":
    # Example usage
    title = "Test Notification"
    message = "This is a test message from the notification system!"
    priority = 0  # Normal priority

    try:
        success = send_notification(title, message, priority)
        if success:
            print("Pushover notification sent successfully!")
        else:
            print("Failed to send Pushover notification")
    except Exception as e:
        print(f"Error sending Pushover notification: {e}")
