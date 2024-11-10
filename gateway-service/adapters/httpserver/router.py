from models import NotificationInfo
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from adapters.rabbithandler import rabbit_producer

router = APIRouter()


#
# class ErrorResponse(BaseModel):
#     detail: str

class SuccessResponse(BaseModel):
    message: str


@router.post("/notify",
             response_model=SuccessResponse)
async def notify_handler(notification: NotificationInfo):
    try:
        message = notification.model_dump(by_alias=True)
        rabbit_producer.send_message(message)
        return SuccessResponse(message="Successfully sent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {e}")