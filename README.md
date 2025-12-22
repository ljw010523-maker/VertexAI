# Vertex AI 기반 보안 챗봇 백엔드

제조업 중소기업(100-200명 규모)을 위한 AI 챗봇 백엔드 시스템입니다. Google Gemini API를 활용하여 안전하고 효율적인 대화형 AI 서비스를 제공합니다.

## 📋 목차

- [프로젝트 개요](#프로젝트-개요)
- [주요 기능](#주요-기능)
- [기술 스택](#기술-스택)
- [시스템 아키텍처](#시스템-아키텍처)
- [설치 및 실행](#설치-및-실행)
- [API 사용법](#api-사용법)
- [보안 기능](#보안-기능)
- [배포 가이드](#배포-가이드)
- [FAQ](#faq)

---

## 🎯 프로젝트 개요

### 목적
- 사내 임직원을 위한 안전한 AI 챗봇 시스템 구축
- 개인정보 보호 및 민감정보 필터링 기능 제공
- 대화 내역 로깅 및 감사 추적(Audit Trail) 지원

### 개발 환경
- **운영체제**: Windows 11
- **Python 버전**: 3.11
- **개발 도구**: VSCode

---

## ✨ 주요 기능

### 1. AI 대화 기능
- **Google Gemini 2.5 Flash** 모델 사용
- 빠른 응답 속도 및 자연스러운 대화
- 무료 티어로 테스트 가능

### 2. 보안 필터링
- **개인정보 자동 탐지 및 마스킹**
  - 이메일 주소
  - 전화번호 (한국 형식 지원)
  - 주민등록번호
  - 신용카드 번호
  - IP 주소

- **민감 키워드 차단**
  - 해킹, 크랙, 불법 등 위험 키워드
  - 관리자 비밀번호, DB 접속정보, API 키 등

### 3. 데이터베이스 로깅
- 모든 대화 내역 SQLite에 저장
- 사용자별 채팅 기록 조회 가능
- PostgreSQL로 마이그레이션 가능

### 4. REST API
- FastAPI 기반의 RESTful API
- Swagger UI 자동 문서화
- CORS 설정으로 프론트엔드 연동 지원

---

## 🛠 기술 스택

### Backend Framework
- **FastAPI** - 고성능 Python 웹 프레임워크
- **Uvicorn** - ASGI 웹 서버
- **Pydantic** - 데이터 검증 및 직렬화

### Database
- **SQLAlchemy** - ORM (Object-Relational Mapping)
- **SQLite** - 개발 환경용 데이터베이스
- **PostgreSQL** - 운영 환경 권장

### AI/ML
- **Google Generative AI** - Gemini API 클라이언트
- **gemini-2.5-flash** - 빠르고 효율적인 AI 모델

### Security
- 정규표현식 기반 PII 탐지
- 키워드 필터링
- 환경변수 기반 설정 관리

---

## 🏗 시스템 아키텍처

```
┌─────────────────┐
│   Frontend      │  (Next.js - 예정)
│  localhost:3000 │
└────────┬────────┘
         │ HTTP/CORS
         ↓
┌─────────────────┐
│   FastAPI       │  ← 현재 구현 완료
│  localhost:8000 │
└────────┬────────┘
         │
    ┌────┴─────┬──────────┐
    ↓          ↓          ↓
┌────────┐ ┌─────────┐ ┌──────────┐
│Security│ │ Gemini  │ │ Database │
│Filter  │ │   API   │ │ (SQLite) │
└────────┘ └─────────┘ └──────────┘
```

### 디렉토리 구조

```
VertexAI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── chat.py              # 채팅 API 엔드포인트
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   ├── database.py          # DB 연결 설정
│   │   │   └── models.py            # DB 모델 정의
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── gemini_api_service.py   # Gemini API 서비스
│   │   │   └── security_filter.py      # 보안 필터링
│   │   └── utils/
│   │       ├── __init__.py
│   │       └── config.py            # 환경 설정
│   ├── main.py                      # FastAPI 메인 앱
│   ├── .env                         # 환경 변수 (git 제외)
│   ├── requirements.txt             # Python 패키지 목록
│   └── venv/                        # 가상환경 (git 제외)
├── .gitignore
└── README.md
```

---

## 🚀 설치 및 실행

### 1. 사전 요구사항
- Python 3.11 이상
- Git

### 2. 저장소 클론
```bash
git clone https://github.com/your-username/VertexAI.git
cd VertexAI/backend
```

### 3. 가상환경 생성 및 활성화

**Windows (PowerShell):**
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```bash
python -m venv venv
venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
python -m venv venv
source venv/bin/activate
```

### 4. 패키지 설치
```bash
pip install -r requirements.txt
```

### 5. 환경 변수 설정

`.env.example` 파일을 복사하여 `.env` 파일 생성:

```bash
cp .env.example .env
```

`.env` 파일 수정:
```env
# Gemini API 키 설정 (필수!)
GEMINI_API_KEY=your-api-key-here

# 데이터베이스 설정
DATABASE_URL=sqlite+aiosqlite:///./chat_logs.db

# 보안 설정
SECRET_KEY=your-secret-key-change-this-in-production
MAX_MESSAGE_LENGTH=2000

# CORS 설정
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# 디버그 모드
DEBUG=true
```

### 6. Gemini API 키 발급

1. [Google AI Studio](https://aistudio.google.com/app/apikey) 접속
2. "Create API Key" 클릭
3. 발급받은 키를 `.env` 파일에 입력

### 7. 서버 실행

**방법 1 - main.py로 실행 (권장):**
```bash
python main.py
```

**방법 2 - uvicorn으로 실행:**
```bash
uvicorn main:app --reload
```

### 8. 서버 확인

브라우저에서 다음 주소로 접속:
- **API 문서 (Swagger UI)**: http://localhost:8000/docs
- **메인 페이지**: http://localhost:8000

서버가 정상 실행되면 다음 메시지가 표시됩니다:
```
[OK] Gemini API 초기화 완료!
==================================================
[서버 시작 완료]
==================================================
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## 📡 API 사용법

### 1. 채팅 API

**Endpoint:** `POST /api/chat`

**Request Body:**
```json
{
  "user_id": "user123",
  "message": "Python에 대해 설명해줘"
}
```

**Response:**
```json
{
  "response": "Python은 고수준의 프로그래밍 언어입니다...",
  "filtered": false,
  "log_id": 1,
  "timestamp": "2025-12-22T12:00:00.000000Z"
}
```

**cURL 예제:**
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "test_user",
    "message": "Hello, AI!"
  }'
```

### 2. 채팅 기록 조회

**Endpoint:** `GET /api/chat/history/{user_id}`

**예제:**
```bash
curl "http://localhost:8000/api/chat/history/user123?limit=10"
```

**Response:**
```json
{
  "user_id": "user123",
  "total_count": 5,
  "logs": [
    {
      "id": 1,
      "message": "안녕하세요",
      "response": "안녕하세요! 무엇을 도와드릴까요?",
      "filtered": false,
      "created_at": "2025-12-22T12:00:00"
    }
  ]
}
```

### 3. Swagger UI에서 테스트

1. http://localhost:8000/docs 접속
2. **POST /api/chat** 엔드포인트 클릭
3. **"Try it out"** 버튼 클릭
4. Request body 입력
5. **Execute** 버튼 클릭
6. 응답 확인

---

## 🔒 보안 기능

### 개인정보 탐지 및 마스킹

사용자가 입력한 메시지에서 개인정보를 자동으로 탐지하고 마스킹합니다.

**탐지 항목:**
```python
# 이메일
"test@example.com" → "***@***.***"

# 전화번호
"010-1234-5678" → "***-****-****"

# 주민등록번호
"901234-1234567" → "******-*******"

# 신용카드 번호
"1234-5678-9012-3456" → "****-****-****-****"

# IP 주소
"192.168.0.1" → "***.***.*.**"
```

### 차단 키워드

다음 키워드가 포함된 메시지는 차단됩니다:
- 해킹, 크랙, 불법, 도용
- 관리자 비밀번호, DB 접속정보, API 키

**차단 시 응답:**
```json
{
  "response": "보안 정책상 해당 요청은 처리할 수 없습니다.",
  "filtered": true,
  "log_id": 10,
  "timestamp": "2025-12-22T12:00:00.000000Z"
}
```

---

## 🌐 배포 가이드

### GCP (Google Cloud Platform) 배포 - 권장

Vertex AI와 최적 통합을 위해 GCP 사용을 권장합니다.

**1. Cloud Run 배포:**
```bash
gcloud run deploy vertexai-chatbot \
  --source . \
  --region asia-northeast3 \
  --allow-unauthenticated
```

**2. 환경 변수 설정:**
```bash
gcloud run services update vertexai-chatbot \
  --set-env-vars GEMINI_API_KEY=your-key
```

### 기타 클라우드 서비스

- **AWS**: Elastic Beanstalk, ECS
- **Azure**: App Service
- **Naver Cloud**: Cloud Functions

### 네트워크 구성 (운영 환경)

```
Internet
   ↓
[Load Balancer]
   ↓
[Nginx] :80/443 (HTTPS)
   ↓
[Uvicorn] :8000 (FastAPI)
   ↓
[PostgreSQL] :5432
```

---

## 💡 FAQ

### Q1. Gemini API 키는 어디서 발급받나요?
**A:** [Google AI Studio](https://aistudio.google.com/app/apikey)에서 무료로 발급받을 수 있습니다.

### Q2. 어떤 모델을 사용하나요?
**A:** 현재 `gemini-2.5-flash` 모델을 사용합니다. 무료이면서도 빠르고 효율적입니다.

### Q3. gemini-pro는 사용할 수 없나요?
**A:** `gemini-pro`와 `gemini-1.5-flash`는 deprecated되었습니다. 무료 모델은 `gemini-2.5-flash`를 사용해야 합니다. `gemini-2.5-pro`는 유료입니다.

### Q4. 운영 환경에서 주의할 점은?
**A:**
- `.env` 파일을 Git에 절대 올리지 마세요
- `DEBUG=false`로 설정하세요
- PostgreSQL을 사용하세요 (SQLite는 개발용)
- HTTPS를 사용하세요 (Nginx + Let's Encrypt)

### Q5. CORS 에러가 발생합니다.
**A:** `.env` 파일의 `ALLOWED_ORIGINS`에 프론트엔드 주소를 추가하세요:
```env
ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.com
```

### Q6. Uvicorn vs FastAPI vs IDC의 차이는?
**A:**
- **FastAPI**: 웹 애플리케이션 프레임워크 (애플리케이션 레이어)
- **Uvicorn**: ASGI 웹 서버 (실행 레이어)
- **IDC**: 물리적 서버가 위치한 데이터센터 (인프라 레이어)

### Q7. `__init__.py` 파일은 왜 필요한가요?
**A:** Python이 해당 디렉토리를 패키지로 인식하게 만듭니다. 이를 통해 `from app.api import chat` 같은 import가 가능해집니다.

### Q8. config.py에 API 키를 넣어야 하나요?
**A:** 아니요! API 키는 `.env` 파일에만 넣으면 됩니다. `config.py`는 자동으로 `.env`에서 읽어옵니다.

### Q9. 프론트엔드는 어떻게 구성하나요?
**A:** Next.js 사용을 권장합니다. 100-200명 규모의 중소기업에 적합하며, React 기반으로 빠른 개발이 가능합니다.

### Q10. 사용 가능한 모델 목록을 확인하려면?
**A:**
```bash
cd backend
python list_models.py  # 모든 사용 가능한 Gemini 모델 조회
```

---

## 🔧 개발 팁

### 서버 자동 재시작
코드 변경 시 서버가 자동으로 재시작되도록 `--reload` 옵션 사용:
```bash
uvicorn main:app --reload
```

### 데이터베이스 초기화
```bash
# SQLite 파일 삭제
rm chat_logs.db

# 서버 재시작 (자동으로 테이블 생성)
python main.py
```

### 로그 확인
서버 실행 중 터미널에 모든 로그가 출력됩니다:
- `[OK]`: 정상 동작
- `[ERROR]`: 오류 발생
- `[INFO]`: 정보성 메시지

---

## 📝 다음 단계

- [ ] 프론트엔드 개발 (Next.js)
- [ ] 사용자 인증/인가 기능 추가
- [ ] Redis 캐싱 적용
- [ ] PostgreSQL로 마이그레이션
- [ ] Vertex AI로 업그레이드 (기업용)
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 구축

---

## 📄 라이선스

MIT License

---

## 👥 기여자

- 개발자: Bravo

---

## 📞 문의

이슈나 질문이 있으시면 GitHub Issues에 등록해주세요.

---

**마지막 업데이트:** 2025-12-22
