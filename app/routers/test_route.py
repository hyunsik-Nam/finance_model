from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from app.database.supabase import get_supabase_client
from app.services.test_service import TestService
from fastapi.responses import StreamingResponse
import json

router = APIRouter()

@router.post("/chat")
def chat_api(
    msg: str,
    service: TestService = Depends()
):
    """챗 api"""
    def generate_stream():
        try:
            # 서비스에서 스트림 데이터를 받아와서 그대로 전달
            for chunk in service.get_test_data(msg):
                yield chunk
        except Exception as e:
            # 에러 발생 시 에러 메시지를 스트림으로 전송
            error_data = {"error": str(e)}
            yield f"data: {json.dumps(error_data, ensure_ascii=False)}\n\n"
    
    return StreamingResponse(
        generate_stream(),
        media_type="text/plain",
        headers={"Cache-Control": "no-cache"}
    )
