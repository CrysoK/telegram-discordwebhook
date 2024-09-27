from pydantic import Field, HttpUrl
from src.settings.base import Settings


class _IBBSettings(Settings):
    KEY: str = Field(
        "",
        description="ImgBB API key",
        examples=[
            "b025164c8669ccc59567604a21b0637c"
        ]
    )
    EXPIRATION: int = Field(
        default=7 * 24 * 60 * 60,
        description="Enable this if you want to force uploads to be auto deleted after certain time (in seconds 60-15552000)",
        examples=[
            60,
            15552000
        ]
    )
    URL: HttpUrl = Field(
        default="https://i.ibb.co/",
    )
    UPLOAD_ENDPOINT: HttpUrl = Field(
        default="https://api.imgbb.com/1/upload",
        description="ImgBB API URL",
    )


IBBSettings = _IBBSettings(_env_prefix="IBB_")
