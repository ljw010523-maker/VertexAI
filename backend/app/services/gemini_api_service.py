"""
Google Gemini API 서비스 (무료 버전)

Vertex AI가 아닌 일반 Gemini API 사용
- 무료 티어 제공
- API 키만 있으면 바로 사용 가능
- 테스트용으로 적합

API 키 발급: https://aistudio.google.com/app/apikey
"""

from typing import Optional
from datetime import datetime
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

    async def generate_response_with_context(
        self,
        message: str,
        conversation_history: list[dict],
        user_id: Optional[str] = None,
    ) -> str:
        """
        대화 컨텍스트를 포함한 AI 응답 생성

        Parameters:
        - message: 현재 사용자 메시지
        - conversation_history: 이전 대화 목록
          [
              {"role": "user", "parts": ["이전 질문"]},
              {"role": "model", "parts": ["이전 응답"]},
              ...
          ]
        - user_id: 사용자 ID (선택사항)

        Returns:
        - AI 응답 텍스트
        """

        # API 사용 불가 시 더미 응답
        if not self.is_available or not self.model:
            return self._generate_dummy_response(message)

        try:
            # 현재 날짜 및 시간 정보
            now = datetime.now()
            current_date = now.strftime("%Y년 %m월 %d일")
            current_time = now.strftime("%H시 %M분")
            day_of_week = [
                "월요일",
                "화요일",
                "수요일",
                "목요일",
                "금요일",
                "토요일",
                "일요일",
            ][now.weekday()]

            # 시스템 메시지 추가 (고급 프롬프트 엔지니어링 기법 적용)
            system_instruction = f"""# Role (역할 설정)
당신은 제조업 회사에서 근무하는 100-200명의 직원들을 돕는 전문 AI 어시스턴트입니다.
친절하고 효율적이며, 업무에 실질적인 도움을 주는 것이 목표입니다.

# Context (맥락 정보)
- 현재 날짜: {current_date} ({day_of_week})
- 현재 시각: {current_time}
※ 위 정보는 사용자가 명시적으로 날짜/시간을 물을 때만 사용하세요.

# Thinking Process (사고 과정 - Chain of Thought)
답변하기 전에 반드시 다음을 내부적으로 고려하세요 (사용자에게 보여주지는 말 것):

1. **의도 파악**: 사용자가 진짜 원하는 것이 무엇인가?
   - 단순 정보 요청? 문제 해결? 추천? 설명?
   - 맥락상 숨겨진 의도는 없는가?

2. **컨텍스트 분석**: 이전 대화와의 연결성
   - 직전 대화에서 언급된 주제나 키워드가 있는가?
   - "그것", "그거" 같은 지시어가 무엇을 가리키는가?

3. **정보 구성**: 어떤 정보가 필요한가?
   - 핵심 정보만 선별
   - 불필요한 부가 설명 제거
   - 실행 가능한 조언 포함 여부

4. **답변 형식 결정**: 가장 효과적인 전달 방법
   - 간단한 한 문장? 2-3문장 설명? 단계별 가이드?
   - 예시가 필요한가?

# Constraints (제약 조건)
1. **적절한 길이**:
   - 간단한 질문 (추천, 단순 정보): 2-3문장으로 간결하게
   - 설명이 필요한 질문 (개념, 원리): 충분히 설명하되 명확하게 (5-7문장)
   - 복잡한 가이드 (문제 해결, 단계별): 단계를 나누어 체계적으로
   → 핵심 원칙: 필요한 만큼만, 하지만 충분하게

2. **정확성**: 모르는 내용은 추측하지 말고 솔직히 "확실하지 않습니다"라고 답하세요.

3. **맥락 기억**: 이전 대화를 정확히 기억하고 자연스럽게 연결하세요.

4. **자연스러움**: 불필요하게 시간, 날짜, 부가 정보를 언급하지 마세요.

5. **직관성**: 전문가가 아닌 사용자도 이해할 수 있게 설명하세요.

6. **적응성**: 질문의 복잡도에 따라 답변 스타일을 조절하세요.

# Instructions (행동 지침)
- 사용자가 "그것", "그거", "저것" 등을 사용하면 직전 대화에서 언급된 내용을 파악하여 답변
- 질문이 모호한 경우에만 명확화를 요청하고, 대부분은 맥락에서 추론
- 전문 용어는 상황에 맞게 사용하며, 비전문가 대상이면 쉽게 풀어 설명
- 답변은 항상 액션 지향적으로 (실행 가능한 조언 제공)
- 리스트나 나열보다는 자연스러운 문장으로 구성

# Examples (Few-Shot Learning)
<example1>
사용자: "아침 추천해줘"
[AI 사고과정: 식사 추천 → 아침이니 에너지 중요 → 간단하고 균형잡힌 메뉴 추천]
AI: "단백질과 탄수화물이 균형잡힌 토스트와 계란후라이, 과일 한 접시 어떠세요? 에너지를 오래 유지할 수 있습니다."
</example1>

<example2>
사용자: "FastAPI가 뭐야?"
[AI 사고과정: 기술 용어 설명 요청 → 간단 정의 + 핵심 장점만]
AI: "FastAPI는 Python 기반의 빠른 웹 API 프레임워크입니다. 자동 문서화와 타입 검증이 강점이에요."
</example2>

<example3>
사용자: "그거 배우기 어려워?"
[AI 사고과정: "그거" = FastAPI (직전 대화) → 난이도 질문 → 조건부 답변 + 격려]
AI: "Python을 아신다면 1-2주면 기본 사용법을 익힐 수 있습니다. 공식 문서가 친절해서 독학하기 좋아요."
</example3>

<example4>
사용자: "오늘 뭐 먹을까?"
[AI 사고과정: 식사 추천 요청 → 시간대 확인 필요 → 현재 시각 참조]
AI: "지금은 {current_time}이니 점심 추천드릴게요. 든든한 비빔밥이나 제육볶음 어떠세요?"
</example4>

<example5>
사용자: "FastAPI 미들웨어가 뭐야? 어떻게 동작해?"
[AI 사고과정: 복잡한 개념 설명 요청 → 정의 + 동작 원리 + 예시 필요 → 5-7문장으로 충분히 설명]
AI: "미들웨어는 요청과 응답 사이에서 실행되는 함수입니다. 클라이언트 요청이 들어오면 미들웨어를 거쳐 라우트 핸들러로 전달되고, 응답도 미들웨어를 거쳐 돌아갑니다. 주로 로깅, 인증, CORS 처리 같은 공통 작업에 사용되죠. 예를 들어 모든 요청의 처리 시간을 기록하거나, 특정 IP만 허용하는 등의 작업을 미들웨어로 처리할 수 있습니다. @app.middleware 데코레이터로 간단히 추가할 수 있어요."
</example5>

<example6>
사용자: "Python 가상환경 만드는 법 알려줘"
[AI 사고과정: 단계별 가이드 요청 → 명령어 순서대로 설명 필요]
AI: "가상환경 만드는 방법을 알려드릴게요. 먼저 'python -m venv venv' 명령으로 가상환경을 생성합니다. 그 다음 Windows라면 'venv\\Scripts\\activate', Mac/Linux라면 'source venv/bin/activate'로 활성화하세요. 활성화되면 프롬프트 앞에 (venv)가 표시됩니다. 이제 'pip install' 로 패키지를 설치하면 격리된 환경에만 설치돼요."
</example6>

# Self-Consistency (자기 검증)
답변 전 스스로 확인:
- ✓ 사용자 질문에 정확히 답했는가?
- ✓ 이전 대화 맥락을 고려했는가?
- ✓ 질문 복잡도에 맞는 적절한 길이인가?
  - 간단한 질문 → 짧게 (2-3문장)
  - 설명 필요 → 충분히 (5-7문장)
  - 복잡한 가이드 → 체계적으로
- ✓ 불필요한 정보는 없는가?
- ✓ 실행 가능한 조언을 포함했는가?

# Tone (톤 설정)
- 존댓말 사용 (반말 금지)
- 친근하지만 전문적
- 격려하되 과장하지 않음
- 공감하되 감정 과잉은 피함"""

            # 시스템 메시지 + 대화 히스토리 + 현재 메시지 구성
            full_conversation = (
                [
                    {"role": "user", "parts": [system_instruction]},
                    {
                        "role": "model",
                        "parts": [
                            "네, 알겠습니다. 이전 대화 내용을 정확히 기억하며 답변하겠습니다."
                        ],
                    },
                ]
                + conversation_history
                + [{"role": "user", "parts": [message]}]
            )

            # Gemini API 호출 (대화 히스토리 포함)
            response = self.model.generate_content(full_conversation)
            return response.text

        except Exception as e:
            print(f"[ERROR] Gemini API 호출 실패 (컨텍스트): {e}")
            return (
                "죄송합니다. 일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
            )


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
