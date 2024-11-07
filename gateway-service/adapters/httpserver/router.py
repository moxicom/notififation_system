from models import NotificationInfo

from fastapi import APIRouter, HTTPException, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from adapters.rabbithandler import rabbit_producer

router = APIRouter()



class ErrorResponse(BaseModel):
    detail: str

class SuccessResponse(BaseModel):
    message: str


@router.post("/notify",
             response_model=SuccessResponse,
             responses={500: {"model": ErrorResponse}})
async def notify_handler(notification: NotificationInfo):
    try:
        message = notification.model_dump(by_alias=True)
        rabbit_producer.send_message(message)
        return SuccessResponse(message="Successfully sent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=ErrorResponse(detail="Failed to send notification: {e}"))