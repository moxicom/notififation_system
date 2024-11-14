from pydantic import BaseModel

class SenderType(BaseModel):
    SMS: bool
    EMAIL: bool


class CallbackType(BaseModel):
    queue: str
    http: str


class NotificationInfo(BaseModel):
    message_id: str
    title: str
    text: str
    from_login: str
    logins: list[str]
    sender_type: SenderType
    callback_type: CallbackType