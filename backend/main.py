"""
FastAPI 메인 애플리케이션

이 파일이 하는 일:
1. FastAPI 앱 생성 및 설정
2. CORS 설정 (프론트엔드 연결 허용)
3. 서버 시작 시 데이터베이스 초기화
4. API 라우터 등록 (나중에 추가)
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.utils.config import settings
from app.database import init_db


# ========================================
# 생명주기 이벤트 (서버 시작/종료 시)
# ========================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    서버 시작/종료 시 실행되는 함수

    - startup: 서버가 시작될 때 DB 초기화
    - shutdown: 서버가 종료될 때 정리 작업
    """
    # === 서버 시작 시 ===
    print("\n" + "=" * 50)
    print("[서버 시작 중...]")
    print("=" * 50)

    # 데이터베이스 초기화
    await init_db()

    print("[OK] FastAPI 서버가 준비되었습니다!")
    print(f"   - 디버그 모드: {settings.DEBUG}")
    print(f"   - 허용 출처: {settings.ALLOWED_ORIGINS}")
    print("=" * 50 + "\n")

    yield  # 서버 실행 (여기서 요청 처리)

    # === 서버 종료 시 ===
    print("\n[서버 종료 중...]")
    # 여기에 정리 작업 추가 가능 (DB 연결 종료 등)


# ========================================
# FastAPI 앱 생성
# ========================================
app = FastAPI(
    title="Vertex AI 보안 챗봇",
    description="보안 강화 AI 챗봇 백엔드",
    version="1.0.0",
    lifespan=lifespan,  # 생명주기 함수 등록
)


# ========================================
# CORS 설정 (프론트엔드 연결 허용)
# ========================================
# CORS = Cross-Origin Resource Sharing
# 다른 주소(localhost:3000)에서 이 서버(localhost:8000)로 요청 허용

allowed_origins = settings.ALLOWED_ORIGINS.split(",")
# "http://localhost:3000,http://localhost:3001" -> 리스트로 변환

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # 허용할 출처 목록
    allow_credentials=True,  # 쿠키 포함 허용
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, PUT, DELETE...)
    allow_headers=["*"],  # 모든 헤더 허용
)


# ========================================
# 기본 엔드포인트 (서버 상태 확인용)
# ========================================
@app.get("/")
async def root():
    """
    서버 상태 확인용 엔드포인트

    브라우저에서 http://localhost:8000 접속 시 응답
    """
    return {
        "status": "ok",
        "message": "Vertex AI 보안 챗봇 서버가 실행 중입니다",
        "version": "1.0.0",
    }


@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트

    로드 밸런서나 모니터링 도구에서 서버 상태 확인용
    """
    return {"status": "healthy", "database": "connected"}


# ========================================
# API 라우터 등록
# ========================================
from app.api import chat

app.include_router(
    chat.router,
    prefix="/api",  # /api/chat 경로로 등록
)


# ========================================
# 서버 실행 (개발용)
# ========================================
if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 50)
    print("[개발 서버 시작]")
    print("=" * 50)
    print("주의: 이 방식은 개발용입니다!")
    print("운영 환경에서는 'uvicorn main:app' 명령 사용")
    print("=" * 50 + "\n")

    # 개발 서버 실행
    uvicorn.run(
        "main:app",  # 실행할 앱
        host="0.0.0.0",  # 모든 IP에서 접속 허용
        port=8000,  # 포트 번호
        reload=True,  # 코드 변경 시 자동 재시작 (개발용)
        log_level="info",  # 로그 레벨
    )
