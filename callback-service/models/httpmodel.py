from pydantic import BaseModel

class Status(BaseModel):
    login: str
    status: bool

class SenderCallback(BaseModel):
    sender_type: str
    message_id: str
    statuses: list[Status]
