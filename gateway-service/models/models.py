from pydantic import BaseModel

class SenderType(BaseModel):
    SMS: bool
    EMAIL: bool


class CallbackType(BaseModel):
    queue: bool
    http: bool


class NotificationInfo(BaseModel):
    from_login: str
    logins: list[str]
    sender_type: SenderType
    callback_type: CallbackType