"""
환경 설정 파일
.env 파일의 내용을 읽어서 Python 객체로 변환합니다.
"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    애플리케이션 설정 클래스

    .env 파일의 변수들을 자동으로 읽어옵니다.
    변수 이름이 .env 파일의 키와 정확히 일치해야 합니다.
    """

    # ========================================
    # 데이터베이스 설정
    # ========================================
    DATABASE_URL: str
    # .env의 DATABASE_URL 값을 자동으로 읽어옴
    # 예: sqlite+aiosqlite:///./chat_logs.db


    # ========================================
    # 보안 설정
    # ========================================
    SECRET_KEY: str
    # 세션, 토큰 암호화에 사용

    MAX_MESSAGE_LENGTH: int = 2000
    # 메시지 최대 길이 (기본값 2000)
    # .env에 없으면 2000 사용


    # ========================================
    # Google Gemini API 설정 (테스트용)
    # ========================================
    GEMINI_API_KEY: Optional[str] = None
    # Gemini API 키 (aistudio.google.com에서 발급)
    # 없으면 더미 모드로 작동


    # ========================================
    # Google Vertex AI 설정 (선택사항)
    # ========================================
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    # Optional = 필수가 아님 (없어도 됨)
    # .env에서 주석처리되어 있으면 None

    VERTEX_AI_LOCATION: Optional[str] = "us-central1"
    # 기본값 설정 (없으면 "us-central1" 사용)

    GEMINI_MODEL: Optional[str] = "gemini-1.5-flash"
    # Gemini 모델 이름


    # ========================================
    # 서버 설정
    # ========================================
    DEBUG: bool = True
    # 디버그 모드 (개발: True, 운영: False)

    ALLOWED_ORIGINS: str = "http://localhost:3000"
    # CORS 허용 주소 (프론트엔드 주소)
    # 여러 개는 쉼표로 구분


    class Config:
        """Pydantic 설정"""
        env_file = ".env"
        # .env 파일 경로 (자동으로 찾음)

        env_file_encoding = "utf-8"
        # 파일 인코딩 (한글 지원)

        case_sensitive = False
        # 대소문자 구분 안 함
        # database_url과 DATABASE_URL 둘 다 인식


# ========================================
# 전역 설정 객체 생성
# ========================================
settings = Settings()
# 이 한 줄로 .env 파일을 읽어서 객체 생성!
# 다른 파일에서 이렇게 사용:
# from app.utils.config import settings
# print(settings.DATABASE_URL)


# ========================================
# 설정값 출력 함수 (디버깅용)
# ========================================
def print_settings():
    """현재 설정값 확인용 함수"""
    print("=" * 50)
    print("[현재 설정값]")
    print("=" * 50)
    print(f"데이터베이스: {settings.DATABASE_URL}")
    print(f"디버그 모드: {settings.DEBUG}")
    print(f"메시지 최대 길이: {settings.MAX_MESSAGE_LENGTH}")
    print(f"허용 출처: {settings.ALLOWED_ORIGINS}")

    if settings.GOOGLE_CLOUD_PROJECT:
        print(f"구글 프로젝트: {settings.GOOGLE_CLOUD_PROJECT}")
    else:
        print("구글 프로젝트: 미설정 (나중에 설정)")

    print("=" * 50)


# 이 파일을 직접 실행하면 설정값 출력
if __name__ == "__main__":
    print_settings()
