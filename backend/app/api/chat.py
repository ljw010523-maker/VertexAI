"""
채팅 API 엔드포인트

이 파일이 하는 일:
1. POST /api/chat - 사용자 메시지 받아서 AI 응답 반환
2. 요청/응답 데이터 검증 (Pydantic 모델)
3. 채팅 로그 DB 저장
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.chat_log import ChatLog
from app.utils.config import settings
from app.services.security_filter import security_filter

# from app.services.vertex_ai_service import vertex_ai_service  # Vertex AI용 (나중에 사용)
from app.services.gemini_api_service import gemini_service  # 테스트용 Gemini API


# ========================================
# APIRouter 생성 (라우터 = 엔드포인트 그룹)
# ========================================
router = APIRouter(
    prefix="/chat",  # 모든 엔드포인트 앞에 /chat 붙음
    tags=["Chat"],  # Swagger에서 그룹 이름
)


# ========================================
# 요청/응답 모델 (Pydantic)
# ========================================
class ChatRequest(BaseModel):
    """
    채팅 요청 모델

    프론트엔드에서 보내는 JSON 형식:
    {
        "user_id": "user123",
        "message": "안녕하세요",
        "use_context": true
    }
    """

    user_id: str = Field(
        ...,  # 필수 항목
        min_length=1,
        max_length=50,
        description="사용자 ID (1~50자)",
        examples=["user123"],
    )

    message: str = Field(
        ...,  # 필수 항목
        min_length=1,
        max_length=2000,
        description="사용자 메시지 (1~2000자)",
        examples=["Vertex AI에 대해 알려줘"],
    )

    use_context: bool = Field(
        default=True,  # 기본값: 컨텍스트 사용
        description="이전 대화 컨텍스트 사용 여부",
        examples=[True],
    )

    context_limit: int = Field(
        default=10,  # 최근 10개 대화 사용 (더 긴 기억)
        ge=1,  # 최소 1
        le=50,  # 최대 50 (긴 대화도 지원)
        description="포함할 이전 대화 개수 (1~50)",
        examples=[10],
    )

    class Config:
        """Pydantic 설정"""

        json_schema_extra = {
            "example": {
                "user_id": "user123",
                "message": "Vertex AI에 대해 알려줘",
                "use_context": True,
                "context_limit": 10,
            }
        }


class ChatResponse(BaseModel):
    """
    채팅 응답 모델

    백엔드에서 프론트로 보내는 JSON 형식:
    {
        "response": "AI 응답 내용",
        "filtered": false,
        "log_id": 1,
        "timestamp": "2024-01-01T12:00:00"
    }
    """

    response: str = Field(
        ...,
        description="AI 응답 메시지",
        examples=["Vertex AI는 구글의 머신러닝 플랫폼입니다."],
    )

    filtered: bool = Field(
        default=False,
        description="보안 필터링 여부 (True면 필터링됨)",
        examples=[False],
    )

    log_id: int = Field(..., description="저장된 로그의 DB ID", examples=[1])

    timestamp: str = Field(
        ...,
        description="응답 생성 시각 (ISO 8601 형식)",
        examples=["2024-01-01T12:00:00.000Z"],
    )

    class Config:
        """Pydantic 설정"""

        json_schema_extra = {
            "example": {
                "response": "Vertex AI는 구글의 머신러닝 플랫폼입니다.",
                "filtered": False,
                "log_id": 1,
                "timestamp": "2024-01-01T12:00:00.000Z",
            }
        }


# ========================================
# 채팅 엔드포인트
# ========================================
@router.post(
    "",  # prefix가 /chat이므로 실제 경로는 /api/chat
    response_model=ChatResponse,
    summary="채팅 메시지 전송",
    description="사용자 메시지를 받아 AI 응답을 반환하고 로그를 저장합니다.",
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    채팅 엔드포인트

    처리 순서:
    1. 요청 데이터 검증 (Pydantic 자동)
    2. 메시지 길이 체크
    3. [나중에] 보안 필터링
    4. [나중에] Vertex AI 호출
    5. 응답 생성
    6. DB에 로그 저장
    7. 응답 반환
    """

    # ========================================
    # 1. 메시지 길이 검증
    # ========================================
    if len(request.message) > settings.MAX_MESSAGE_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"메시지가 너무 깁니다 (최대 {settings.MAX_MESSAGE_LENGTH}자)",
        )

    # ========================================
    # 2. 보안 필터링
    # ========================================
    filter_result = security_filter.filter_message(request.message)

    # 필터링된 메시지 사용 (PII 마스킹 적용)
    filtered_message = filter_result.masked_text
    filtered = filter_result.is_filtered

    # 감지된 항목 로깅
    if filter_result.detected_items:
        print(f"[SECURITY] 감지된 항목: {', '.join(filter_result.detected_items)}")
        print(f"[SECURITY] 사유: {filter_result.reason}")

    # ========================================
    # 3. 이전 대화 가져오기 (컨텍스트)
    # ========================================
    conversation_history = []

    if request.use_context:
        # DB에서 최근 대화 가져오기
        from sqlalchemy import select

        stmt = (
            select(ChatLog)
            .where(ChatLog.user_id == request.user_id)
            .order_by(ChatLog.created_at.desc())
            .limit(request.context_limit)
        )
        result = await db.execute(stmt)
        recent_chats = result.scalars().all()

        # 시간 순서대로 정렬 (오래된 것부터)
        recent_chats = list(reversed(recent_chats))

        # Gemini API 형식으로 변환
        for chat in recent_chats:
            conversation_history.append({
                "role": "user",
                "parts": [chat.message]
            })
            conversation_history.append({
                "role": "model",
                "parts": [chat.response]
            })

        print(f"[CONTEXT] {len(recent_chats)}개의 이전 대화 로드됨")

    # ========================================
    # 4. AI 응답 생성 (Vertex AI)
    # ========================================
    # 금지 키워드가 감지되었다면 차단
    if filtered:
        ai_response = (
            "죄송합니다. 보안 정책에 위배되는 내용이 포함되어 있어 응답할 수 없습니다."
        )
    else:
        # Gemini API 호출 (컨텍스트 포함)
        if conversation_history:
            # 컨텍스트가 있으면 히스토리와 함께 전달
            ai_response = await gemini_service.generate_response_with_context(
                message=filtered_message,
                conversation_history=conversation_history,
                user_id=request.user_id,
            )
        else:
            # 컨텍스트 없으면 일반 응답
            ai_response = await gemini_service.generate_response(
                message=filtered_message,
                user_id=request.user_id,
            )

    # ========================================
    # 4. DB에 로그 저장
    # ========================================
    try:
        # ChatLog 객체 생성
        # 주의: 마스킹된 메시지를 저장 (개인정보 보호)
        chat_log = ChatLog(
            user_id=request.user_id,
            message=filtered_message,  # 마스킹된 메시지 저장
            response=ai_response,
            filtered=filtered,
            created_at=datetime.utcnow(),
        )

        # DB에 추가
        db.add(chat_log)
        await db.commit()
        await db.refresh(chat_log)

        print(
            f"[OK] 채팅 로그 저장 완료! (log_id={chat_log.id}, user={request.user_id})"
        )

    except Exception as e:
        await db.rollback()
        print(f"[ERROR] DB 저장 실패: {e}")
        raise HTTPException(status_code=500, detail="채팅 로그 저장에 실패했습니다")

    # ========================================
    # 5. 응답 반환
    # ========================================
    return ChatResponse(
        response=ai_response,
        filtered=filtered,
        log_id=chat_log.id,
        timestamp=chat_log.created_at.isoformat() + "Z",
    )


# ========================================
# 채팅 기록 조회 엔드포인트 (추가 기능)
# ========================================
@router.get(
    "/history/{user_id}",
    summary="채팅 기록 조회",
    description="특정 사용자의 채팅 기록을 조회합니다.",
)
async def get_chat_history(
    user_id: str,
    limit: int = 10,  # 최근 10개만
    db: AsyncSession = Depends(get_db),
):
    """
    채팅 기록 조회

    Parameters:
    - user_id: 조회할 사용자 ID
    - limit: 가져올 최대 개수 (기본 10개)
    """
    from sqlalchemy import select

    try:
        # 최근 채팅 기록 조회 (created_at 내림차순)
        stmt = (
            select(ChatLog)
            .where(ChatLog.user_id == user_id)
            .order_by(ChatLog.created_at.desc())
            .limit(limit)
        )

        result = await db.execute(stmt)
        logs = result.scalars().all()

        # 딕셔너리 리스트로 변환
        return {
            "user_id": user_id,
            "count": len(logs),
            "history": [log.to_dict() for log in logs],
        }

    except Exception as e:
        print(f"[ERROR] 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail="채팅 기록 조회에 실패했습니다")
