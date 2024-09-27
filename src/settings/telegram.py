from typing import NoReturn

from pydantic import BaseModel, Field, HttpUrl

from src.settings.base import Settings


class TelegramChatSettings(BaseModel):
    id: int = Field(
        ...,
        description="Telegram channel ID",
        examples=[5678]
    )
    ignore_users: list[str] = Field(
        [],
        description="Ignore channel users",
        examples=["abc123_bot"]
    )
    webhooks: list[HttpUrl] = Field(
        ...,
        description="Webhook URLs",
        examples=["https://discord.com/api/webhooks/9012/wxyz"]
    )


class _TelegramSettings(Settings):
    API_ID: int = Field(
        ...,
        description="Telegram user API ID",
        examples=[12345678]
    )
    API_HASH: str = Field(
        ...,
        description="Telegram user API hash (MD5)",
        examples=["af1b88ca9fd8a3e828b40ed1b9a2cb20"]
    )
    IMAGE_MAX_SIZE: int = Field(
        10 * 1024 * 1024,
        description="Telegram image max size (in megabytes)",
        examples=[10, 1024]
    )
    CHATS: list[TelegramChatSettings] = Field(
        ...,
        examples=[
            [
                {
                    "id": 5678,
                    "ignore_users": ["abc123_bot"],
                    "webhooks": ["https://discord.com/api/webhooks/9012/wxyz"]
                }
            ]
        ]
    )

    @classmethod
    def get_chat(cls, id: int) -> TelegramChatSettings:
        for chat in cls.CHATS:
            if chat.ID == id:
                return chat



TelegramSettings = _TelegramSettings(_env_prefix="TELEGRAM_")
