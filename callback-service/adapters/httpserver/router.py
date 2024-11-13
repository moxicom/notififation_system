import redis

from adapters.redis import get_redis_client
from adapters.redis import RedisClient
from models import SenderCallback
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from models.models import NotificationDBStatus

router = APIRouter()


#
# class ErrorResponse(BaseModel):
#     detail: str

@router.post("/callback")
async def notify_handler(callback: SenderCallback, redis_client: RedisClient = Depends(get_redis_client)):
    try:
        db_statuses = redis_client.get_data(callback.message_id)
        for db_idx in range(len(db_statuses)):
            for cb_idx in range(len(callback.statuses)):
                if (db_statuses[db_idx].sender_type == callback.sender_type and
                        db_statuses[db_idx].login == callback.statuses[cb_idx].login):
                    db_statuses[db_idx].status = callback.statuses[cb_idx].status

        redis_client.set_data(callback.message_id, db_statuses)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process shit: {e}")