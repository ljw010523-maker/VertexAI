"""
Google Gemini API 서비스 (무료 버전)

Vertex AI가 아닌 일반 Gemini API 사용
- 무료 티어 제공
- API 키만 있으면 바로 사용 가능
- 테스트용으로 적합

API 키 발급: https://aistudio.google.com/app/apikey
"""

from typing import Optional
import google.generativeai as genai
from app.utils.config import settings


# ========================================
# Gemini API 서비스 클래스
# ========================================
class GeminiAPIService:
    """Google Gemini API 호출 서비스"""

    def __init__(self, api_key: Optional[str] = None):
        """
        초기화

        Parameters:
        - api_key: Gemini API 키 (.env의 GEMINI_API_KEY)
        """
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.is_available = False
        self.model = None

        # API 키가 있으면 초기화
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel("gemini-2.5-flash")
                self.is_available = True
                print("[OK] Gemini API 초기화 완료!")
            except Exception as e:
                print(f"[ERROR] Gemini API 초기화 실패: {e}")
                self.is_available = False
        else:
            print(
                "[INFO] GEMINI_API_KEY가 설정되지 않았습니다. 더미 모드로 작동합니다."
            )

    async def generate_response(
        self,
        message: str,
        user_id: Optional[str] = None,
    ) -> str:
        """
        AI 응답 생성

        Parameters:
        - message: 사용자 메시지
        - user_id: 사용자 ID (선택사항)

        Returns:
        - AI 응답 텍스트
        """

        # API 사용 불가 시 더미 응답
        if not self.is_available or not self.model:
            return self._generate_dummy_response(message)

        try:
            # Gemini API 호출
            response = self.model.generate_content(message)
            return response.text

        except Exception as e:
            print(f"[ERROR] Gemini API 호출 실패: {e}")
            return (
                "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            )

    def _generate_dummy_response(self, message: str) -> str:
        """더미 응답 생성 (API 키 없을 때)"""
        message_lower = message.lower()

        if "안녕" in message_lower or "hello" in message_lower:
            return "안녕하세요! 저는 AI 챗봇입니다. 무엇을 도와드릴까요?"

        elif "vertex ai" in message_lower or "gemini" in message_lower:
            return """Gemini는 구글의 최신 AI 모델입니다.

주요 특징:
1. 멀티모달 AI (텍스트, 이미지, 영상 처리)
2. 빠른 응답 속도
3. 무료 티어 제공

현재 더미 모드로 작동 중입니다.
.env에 GEMINI_API_KEY를 추가하면 실제 AI 응답을 받을 수 있습니다."""

        else:
            return f"""'{message}'에 대해 질문하셨군요.

[더미 응답 모드]
실제 Gemini AI를 사용하려면:
1. https://aistudio.google.com/app/apikey 에서 API 키 발급
2. .env 파일에 GEMINI_API_KEY=your-api-key 추가
3. 서버 재시작

이후 실제 AI 응답으로 전환됩니다."""


# ========================================
# 전역 서비스 인스턴스
# ========================================
gemini_service = GeminiAPIService()


# ========================================
# 테스트 함수
# ========================================
async def test_gemini():
    """Gemini API 테스트"""
    print("=" * 50)
    print("[Gemini API 테스트]")
    print("=" * 50)

    test_messages = [
        "안녕하세요",
        "Python에 대해 간단히 설명해줘",
        "FastAPI의 장점은?",
    ]

    for msg in test_messages:
        print(f"\n사용자: {msg}")
        response = await gemini_service.generate_response(msg)
        print(f"AI: {response}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_gemini())
