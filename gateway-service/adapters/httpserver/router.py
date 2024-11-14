import logging

import httpx

from core.config import config
from models import NotificationInfo
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from adapters.rabbithandler import rabbit_producer

router = APIRouter()

LOGGER = logging.getLogger(__name__)


#
# class ErrorResponse(BaseModel):
#     detail: str

class SuccessResponse(BaseModel):
    message: str

bearer_scheme = HTTPBearer()


async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)):
    token = credentials.credentials
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing token")

    token = token.split(' ')[1]
    LOGGER.info("token", token)

    async with httpx.AsyncClient() as client:
        response = await client.post(config.AUTH_SERVICE_URL+"/api/v1/validate_token", headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200 and response.status_code != 500:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token")
    if response.status_code == 500:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="internal error")


@router.post("/notify", response_model = SuccessResponse, dependencies=[Depends(verify_token)])
async def notify_handler(notification: NotificationInfo):
    try:
        message = notification.model_dump(by_alias=True)
        rabbit_producer.send_message(message)
        return SuccessResponse(message="Successfully sent")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send notification: {e}")