from pydantic import BaseModel
from dataclasses import dataclass
import json
from typing import Any


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

@dataclass
class NotificationDBStatus:
    message_id: str
    login: str
    sender_type: str
    status: bool

    def  __init__(self, message_id: str, login: str, sender_type: str, status: bool):
        self.message_id = message_id
        self.login = login
        self.sender_type = sender_type
        self.status = status

    def to_json(self) -> str:
        """Convert the model to a JSON string for storage in Redis."""
        return json.dumps(self.__dict__)

    @staticmethod
    def from_json(data: str) -> 'NotificationDBStatus':
        """Create a User instance from a JSON string."""
        return NotificationDBStatus(**json.loads(data))