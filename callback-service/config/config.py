import os
from email.policy import default


class Config:
    SERVER_PORT: int = int(os.getenv("CALLBACK_PORT", default=8080))

    RABBIT_HOST: str = os.getenv("RABBIT_HOST", default="localhost")
    RABBIT_USER: str = os.getenv("RABBIT_USER", default="rmuser")
    RABBIT_PASSWORD: str = os.getenv("RABBIT_PASSWORD", default="rmpassword")

    REDIS_HOST: str = os.getenv("REDIS_HOST", default="localhost")
    REDIS_PORT: str = os.getenv("REDIS_PORT", default="6379")

    INPUT_QUEUE: str = os.getenv("CALLBACK_SERV_QUEUE", default="cb_queue")

    MAIL_SENDER_URL: str = os.getenv("MAIL_SENDER_URL", default="http://localhost:8081/default")
    SMS_SENDER_URL: str = os.getenv("SMS_SENDER_URL", default="http://localhost:8081/default")

    CALLBACK_SERVICE_TIMEOUT: int = int(os.getenv("CALLBACK_SERVICE_TIMEOUT", default=10))
    CALLBACK_SERVICE_RABBIT_TTL: int = int(os.getenv("CALLBACK_SERVICE_RABBIT_TTL", default=15))

config = Config()