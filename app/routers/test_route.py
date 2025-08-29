from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.database.supabase import get_supabase_client
from app.services.test_service import TestService
from fastapi.responses import StreamingResponse
import json

router = APIRouter()
testService = TestService()

@router.post("/chat")
async def chat_api(msg: str):
    """챗 api"""
    async def event_stream():
        async for chunk in testService.get_test_data(msg):
            yield chunk

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache"}
    )

@router.get("/ping")
async def ping():
    return {"message": "pong"}
