import os

class Config:
    SERVER_PORT: int = int(os.getenv("GATEWAY_PORT", default=8081))
    RABBIT_HOST: str = os.getenv("RABBIT_HOST", default="localhost")
    RABBIT_USER: str = os.getenv("RABBIT_USER", default="rmuser")
    RABBIT_PASSWORD: str = os.getenv("RABBIT_PASSWORD", default="rmpassword")
    CALLBACK_SERV_QUEUE: str = os.getenv("CALLBACK_SERV_QUEUE", default="callback_input")
    GATEWAY_INPUT_QUEUE: str = os.getenv("GATEWAY_INPUT_QUEUE", default="gateway_input")


config = Config()