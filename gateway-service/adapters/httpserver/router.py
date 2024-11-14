import httpx

from core.config import config
from models import NotificationInfo
from fastapi import APIRouter, HTTPException, Request, status, Depends
from pydantic import BaseModel
from adapters.rabbithandler import rabbit_producer

router = APIRouter()


#
# class ErrorResponse(BaseModel):
#     detail: str

class SuccessResponse(BaseModel):
    message: str


async def verify_token(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    token_value = token.split(" ")[1]

    async with httpx.AsyncClient() as client:
        response = await client.get(
            config.AUTH_SERVICE_URL+"/api/v1/login",
            headers={"Authorization": f"Bearer {token_value}"}
        )

    if response.status_code != 200 and response.status_code != 500:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    if response.status_code == 500:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal error")


@router.post("/notify", response_model = SuccessResponse)
async def notify_handler(notification: NotificationInfo, token_verified: bool = Depends(verify_token)):
    try:
        message = notification.model_dump(by_alias=True)
        rabbit_producer.send_message(message)
        return SuccessResponse(message="Successfully sent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {e}")