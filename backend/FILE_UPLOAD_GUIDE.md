# 파일 업로드 기능 구현 가이드

## 현재 상태 vs 파일 업로드

### 현재 (텍스트만)
```
사용자: "파이썬이 뭐야?"
AI: "파이썬은 프로그래밍 언어입니다..."
```

### 파일 업로드 추가 후
```
사용자: [이미지 업로드] + "이 그림 뭐야?"
AI: "이 그림은 파이썬 로고입니다..."

사용자: [PDF 업로드] + "이 문서 요약해줘"
AI: "이 문서는 제품 매뉴얼이며..."
```

---

## 구현 방법

### 1단계: 백엔드에 파일 업로드 엔드포인트 추가

#### chat.py에 추가할 코드

```python
from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form
from typing import Optional
import google.generativeai as genai
from pathlib import Path
import tempfile

# ========================================
# 파일 업로드 + 채팅 엔드포인트
# ========================================
@router.post(
    "/upload",
    response_model=ChatResponse,
    summary="파일과 함께 채팅",
    description="이미지, PDF 등 파일을 업로드하고 질문합니다.",
)
async def chat_with_file(
    user_id: str = Form(...),
    message: str = Form(...),
    file: UploadFile = File(...),
    use_context: bool = Form(default=True),
    db: AsyncSession = Depends(get_db),
):
    """
    파일 업로드 + 채팅

    지원 파일:
    - 이미지: jpg, png, gif, webp
    - 문서: pdf
    - 동영상: mp4, avi, mov (Gemini Pro Vision)
    """

    # 파일 크기 제한 (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    # 파일 읽기
    file_content = await file.read()

    if len(file_content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"파일 크기는 10MB 이하여야 합니다 (현재: {len(file_content)/1024/1024:.1f}MB)"
        )

    # 지원 파일 타입 확인
    allowed_types = {
        "image/jpeg", "image/png", "image/gif", "image/webp",
        "application/pdf",
        "video/mp4", "video/avi", "video/quicktime"
    }

    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"지원하지 않는 파일 형식입니다: {file.content_type}"
        )

    # 임시 파일로 저장
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        tmp.write(file_content)
        tmp_path = tmp.name

    try:
        # Gemini API로 파일 업로드
        uploaded_file = genai.upload_file(tmp_path)

        # AI 응답 생성 (파일 포함)
        ai_response = await gemini_service.generate_response_with_file(
            message=message,
            uploaded_file=uploaded_file,
            user_id=user_id,
        )

        # DB에 로그 저장
        chat_log = ChatLog(
            user_id=user_id,
            message=f"[파일: {file.filename}] {message}",
            response=ai_response,
            filtered=False,
            created_at=datetime.utcnow(),
        )

        db.add(chat_log)
        await db.commit()
        await db.refresh(chat_log)

        return ChatResponse(
            response=ai_response,
            filtered=False,
            log_id=chat_log.id,
            timestamp=chat_log.created_at.isoformat() + "Z",
        )

    finally:
        # 임시 파일 삭제
        Path(tmp_path).unlink(missing_ok=True)
```

---

### 2단계: Gemini 서비스에 파일 처리 메서드 추가

#### gemini_api_service.py에 추가

```python
async def generate_response_with_file(
    self,
    message: str,
    uploaded_file,
    user_id: Optional[str] = None,
) -> str:
    """
    파일과 함께 AI 응답 생성

    Parameters:
    - message: 사용자 메시지
    - uploaded_file: Gemini에 업로드된 파일 객체
    - user_id: 사용자 ID

    Returns:
    - AI 응답 텍스트
    """
    if not self.is_available or not self.model:
        return "파일 처리 기능은 API 키가 설정되어야 사용 가능합니다."

    try:
        # 파일 + 텍스트를 함께 Gemini에 전달
        response = self.model.generate_content([
            uploaded_file,  # 파일 먼저
            message,        # 그 다음 질문
        ])

        return response.text

    except Exception as e:
        print(f"[ERROR] Gemini API 파일 처리 실패: {e}")
        return "파일 처리 중 오류가 발생했습니다. 다시 시도해주세요."
```

---

### 3단계: 프론트엔드에서 파일 전송

#### React/Next.js 예시

```typescript
// 파일 업로드 컴포넌트
const ChatWithFile = () => {
  const [file, setFile] = useState<File | null>(null);
  const [message, setMessage] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async () => {
    if (!file || !message) return;

    // FormData 생성
    const formData = new FormData();
    formData.append("user_id", "user123");
    formData.append("message", message);
    formData.append("file", file);
    formData.append("use_context", "true");

    // 백엔드로 전송
    const response = await fetch("http://localhost:8000/api/chat/upload", {
      method: "POST",
      body: formData, // JSON 아님! FormData
    });

    const result = await response.json();
    console.log("AI 응답:", result.response);
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*,application/pdf"
        onChange={handleFileChange}
      />
      <input
        type="text"
        value={message}
        onChange={(e) => setMessage(e.target.value)}
        placeholder="파일에 대해 질문하세요"
      />
      <button onClick={handleSubmit}>전송</button>
    </div>
  );
};
```

---

## 사용 예시

### 1. 이미지 질문
```
파일: company_chart.png
질문: "이 조직도에서 개발팀은 어디에 있어?"

AI 응답: "조직도를 보니 개발팀은 기술본부 아래에 위치하고 있으며,
         프론트엔드팀과 백엔드팀으로 나뉘어져 있습니다."
```

### 2. PDF 문서 분석
```
파일: product_manual.pdf
질문: "이 매뉴얼의 안전 주의사항을 요약해줘"

AI 응답: "안전 주의사항은 다음과 같습니다:
         1. 작업 전 전원 차단 확인
         2. 보호 장비 착용 필수
         3. 정기 점검 주기 준수..."
```

### 3. 스크린샷 분석
```
파일: error_screenshot.png
질문: "이 에러 어떻게 해결해?"

AI 응답: "스크린샷에 보이는 에러는 'Database connection failed'입니다.
         다음을 확인하세요:
         1. 데이터베이스 서버가 실행 중인지
         2. .env 파일의 DATABASE_URL이 올바른지..."
```

---

## 고급 기능: 멀티모달 대화

### 파일 + 컨텍스트 결합

```python
async def generate_response_with_file_and_context(
    self,
    message: str,
    uploaded_file,
    conversation_history: list[dict],
    user_id: Optional[str] = None,
) -> str:
    """파일 + 이전 대화 컨텍스트 모두 활용"""

    # 대화 히스토리 + 시스템 메시지
    full_conversation = [
        {"role": "user", "parts": [system_instruction]},
        {"role": "model", "parts": ["네, 알겠습니다."]},
    ] + conversation_history

    # 파일 + 현재 질문 추가
    full_conversation.append({
        "role": "user",
        "parts": [uploaded_file, message]  # 파일과 텍스트 함께
    })

    response = self.model.generate_content(full_conversation)
    return response.text
```

**사용 예:**
```
[이전 대화]
사용자: "우리 제품 A 사양이 뭐야?"
AI: "제품 A는 100kg, 2m 크기입니다"

[현재]
파일: product_a_image.jpg 업로드
사용자: "이게 제품 A야?"

AI: "네, 맞습니다. 앞서 말씀드린 100kg, 2m 크기의 제품 A가 맞습니다.
     사진에서 보이는 것처럼 스테인리스 재질로 되어 있네요."
```

---

## 제한사항 및 고려사항

### 파일 크기 제한
```python
# 무료 티어
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Vertex AI (유료)
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
```

### API 비용
```
텍스트만: $0.000125 / 1K 입력 토큰
이미지: ~258 토큰으로 계산 (~$0.03 per image)
PDF: 페이지당 ~1000 토큰
```

### 지원 파일 형식

| 타입 | 형식 | 모델 |
|------|------|------|
| 이미지 | PNG, JPG, WEBP, GIF | gemini-2.5-flash |
| 문서 | PDF | gemini-2.5-flash |
| 동영상 | MP4, AVI, MOV | gemini-2.5-pro |
| 오디오 | MP3, WAV | gemini-2.5-pro |

---

## 보안 고려사항

### 1. 파일 검증
```python
# 악성 파일 차단
import magic

def validate_file(file_path):
    # MIME 타입 확인 (확장자 속임수 방지)
    mime = magic.from_file(file_path, mime=True)

    if mime not in ALLOWED_MIMES:
        raise ValueError("허용되지 않은 파일 형식")

    # 파일 크기 확인
    if os.path.getsize(file_path) > MAX_SIZE:
        raise ValueError("파일이 너무 큽니다")
```

### 2. 바이러스 스캔 (선택)
```python
# ClamAV 같은 바이러스 스캐너 사용
import pyclamd

cd = pyclamd.ClamdUnixSocket()
scan_result = cd.scan_file(file_path)

if scan_result:
    raise ValueError("악성 파일 감지")
```

### 3. 임시 파일 자동 삭제
```python
# 처리 후 즉시 삭제
try:
    result = process_file(tmp_path)
finally:
    Path(tmp_path).unlink(missing_ok=True)
```

---

## 구현 우선순위

### Phase 1: 이미지만 (가장 간단)
```
✅ 이미지 업로드 (PNG, JPG)
✅ 기본 질문 답변
```

### Phase 2: PDF 추가
```
✅ PDF 업로드
✅ 문서 요약
✅ 특정 페이지 검색
```

### Phase 3: 고급 기능
```
✅ 동영상 분석
✅ 파일 + 컨텍스트 결합
✅ 다중 파일 업로드
```

---

## 실제 사용 시나리오 (제조업)

### 1. 안전 교육
```
직원: [안전 표지판 사진] "이 표시 무슨 뜻이야?"
AI: "이것은 '고압 전기 위험' 표지판입니다. 절대 접근하지 마세요."
```

### 2. 기계 매뉴얼
```
직원: [매뉴얼 PDF] "이 기계 점검 주기는?"
AI: "매뉴얼 23페이지에 따르면 월 1회 점검이 필요합니다."
```

### 3. 에러 해결
```
직원: [기계 에러 화면 스크린샷] "이 에러 어떻게 고쳐?"
AI: "E-102 에러는 센서 불량입니다. A/S 센터에 연락하세요."
```

---

## 요약

**파일 업로드 구현은:**
1. ✅ **기술적으로 가능** (Gemini API 지원)
2. ✅ **구현 난이도 중간** (백엔드 하루, 프론트 하루)
3. ⚠️ **비용 증가** (이미지당 ~$0.03)
4. ⚠️ **보안 주의** (파일 검증 필수)

**추천:**
- Phase 1 완성 후 추가
- 이미지만 먼저 시작
- 사용자 피드백 보고 PDF 추가
