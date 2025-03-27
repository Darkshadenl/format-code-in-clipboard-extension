from pydantic import BaseSettings
import telegram
from dotenv import load_dotenv
import asyncio

# Load environment variables
load_dotenv()


class TelegramSettings(BaseSettings):
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_CHAT_ID: str

    class Config:
        env_file = ".env"


async def send_telegram_message(message: str) -> None:
    settings = TelegramSettings()
    bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
    await bot.send_message(chat_id=settings.TELEGRAM_CHAT_ID, text=message)


if __name__ == "__main__":
    # Example usage
    message = "This is a test message from the notification system!"

    try:
        asyncio.run(send_telegram_message(message))
        print("Telegram message sent successfully!")
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")
