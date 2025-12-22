"""
Vertex AI (Gemini) 서비스

이 파일이 하는 일:
1. Google Vertex AI Gemini 모델 호출
2. 사용자 메시지를 AI에 전달하고 응답 받기
3. 에러 처리 및 재시도 로직

현재 상태: API 키 없이도 테스트 가능하도록 더미 모드 지원
"""

from typing import Optional
from app.utils.config import settings


# ========================================
# Vertex AI 클라이언트 초기화 (나중에 활성화)
# ========================================
# 주석 해제 조건:
# 1. requirements.txt에서 google-cloud-aiplatform 주석 해제
# 2. pip install google-cloud-aiplatform
# 3. .env에 GOOGLE_CLOUD_PROJECT 설정
# 4. GCP 인증 완료

# from google.cloud import aiplatform
# from vertexai.preview.generative_models import GenerativeModel

# # Vertex AI 초기화
# aiplatform.init(
#     project=settings.GOOGLE_CLOUD_PROJECT,
#     location=settings.VERTEX_AI_LOCATION,
# )

# # Gemini 모델 생성
# model = GenerativeModel(settings.GEMINI_MODEL)


# ========================================
# Vertex AI 서비스 클래스
# ========================================
class VertexAIService:
    """Vertex AI (Gemini) 호출 서비스"""

    def __init__(self):
        """초기화"""
        self.is_available = self._check_availability()
        self.model_name = settings.GEMINI_MODEL if settings.GEMINI_MODEL else "gemini-1.5-flash"


    def _check_availability(self) -> bool:
        """
        Vertex AI 사용 가능 여부 확인

        Returns:
        - True: API 키 설정되어 사용 가능
        - False: API 키 없음, 더미 모드 사용
        """
        if not settings.GOOGLE_CLOUD_PROJECT:
            print("[INFO] Vertex AI 미설정 - 더미 모드로 작동합니다")
            return False

        # TODO: 실제 API 연결 테스트
        # try:
        #     # 간단한 테스트 호출
        #     return True
        # except Exception as e:
        #     print(f"[WARNING] Vertex AI 연결 실패: {e}")
        #     return False

        return False


    async def generate_response(
        self,
        message: str,
        user_id: Optional[str] = None,
    ) -> str:
        """
        AI 응답 생성 (메인 함수)

        Parameters:
        - message: 사용자 메시지 (이미 마스킹 처리됨)
        - user_id: 사용자 ID (선택사항, 컨텍스트 관리용)

        Returns:
        - AI 응답 텍스트
        """

        # ========================================
        # Vertex AI 사용 불가 시 더미 응답
        # ========================================
        if not self.is_available:
            return self._generate_dummy_response(message)


        # ========================================
        # Vertex AI 호출 (나중에 활성화)
        # ========================================
        try:
            # TODO: 실제 Vertex AI 호출로 교체
            # response = model.generate_content(
            #     contents=[message],
            #     generation_config={
            #         "temperature": 0.7,  # 창의성 (0.0 ~ 1.0)
            #         "top_p": 0.9,        # 다양성
            #         "top_k": 40,         # 샘플링 범위
            #         "max_output_tokens": 1024,  # 최대 응답 길이
            #     },
            # )
            #
            # return response.text

            # 현재는 더미 응답 반환
            return self._generate_dummy_response(message)

        except Exception as e:
            print(f"[ERROR] Vertex AI 호출 실패: {e}")
            # 에러 발생 시 안전한 응답 반환
            return "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."


    def _generate_dummy_response(self, message: str) -> str:
        """
        더미 응답 생성 (테스트용)

        실제 Gemini API 없이도 작동하도록 간단한 응답 생성
        """
        # 간단한 키워드 기반 응답
        message_lower = message.lower()

        if "안녕" in message_lower or "hello" in message_lower:
            return "안녕하세요! 저는 Vertex AI 기반 보안 챗봇입니다. 무엇을 도와드릴까요?"

        elif "vertex ai" in message_lower or "gemini" in message_lower:
            return """Vertex AI는 구글 클라우드의 머신러닝 플랫폼입니다.

주요 기능:
1. Gemini 모델을 통한 대화형 AI
2. 기업용 보안 및 규정 준수
3. 커스터마이징 가능한 AI 모델

현재 이 챗봇은 Gemini 모델을 사용할 예정입니다."""

        elif "도움" in message_lower or "help" in message_lower:
            return "무엇을 도와드릴까요? 궁금하신 점을 자유롭게 질문해주세요!"

        else:
            return f"""'{message}'에 대해 질문하셨군요.

[더미 응답 모드]
현재 Vertex AI API가 설정되지 않아 더미 응답을 제공하고 있습니다.

실제 Gemini AI를 사용하려면:
1. GCP 프로젝트 생성
2. Vertex AI API 활성화
3. 인증 키 설정
4. .env 파일에 GOOGLE_CLOUD_PROJECT 추가

이후 실제 AI 응답으로 전환됩니다."""


    async def generate_response_with_context(
        self,
        message: str,
        conversation_history: list[dict],
    ) -> str:
        """
        대화 컨텍스트를 포함한 응답 생성 (추가 기능)

        Parameters:
        - message: 현재 메시지
        - conversation_history: 이전 대화 기록
          [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Returns:
        - AI 응답
        """

        if not self.is_available:
            return self._generate_dummy_response(message)

        try:
            # TODO: 대화 기록 포함 API 호출
            # contents = []
            # for msg in conversation_history:
            #     contents.append(msg)
            # contents.append({"role": "user", "content": message})
            #
            # response = model.generate_content(contents=contents)
            # return response.text

            return self._generate_dummy_response(message)

        except Exception as e:
            print(f"[ERROR] Vertex AI 호출 실패 (컨텍스트): {e}")
            return "죄송합니다. 일시적인 오류가 발생했습니다."


# ========================================
# 전역 서비스 인스턴스
# ========================================
vertex_ai_service = VertexAIService()


# ========================================
# 테스트 함수
# ========================================
async def test_vertex_ai():
    """Vertex AI 서비스 테스트"""
    print("=" * 50)
    print("[Vertex AI 서비스 테스트]")
    print("=" * 50)

    test_messages = [
        "안녕하세요",
        "Vertex AI에 대해 알려줘",
        "도움말을 보여줘",
        "테스트 메시지입니다",
    ]

    for msg in test_messages:
        print(f"\n사용자: {msg}")
        response = await vertex_ai_service.generate_response(msg)
        print(f"AI: {response}")

    print("\n" + "=" * 50)


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_vertex_ai())
