"""
채팅 로그 데이터베이스 모델

사용자의 모든 대화 내용을 저장하는 테이블 정의
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.orm import declarative_base
from datetime import datetime


# Base 클래스 생성 (모든 모델의 부모)
Base = declarative_base()


class ChatLog(Base):
    """
    채팅 로그 테이블

    사용자의 질문과 AI 응답을 모두 기록합니다.
    보안 감사 로그로 사용됩니다.
    """

    # 테이블 이름
    __tablename__ = "chat_logs"


    # ========================================
    # 컬럼 정의 (엑셀의 열과 같음)
    # ========================================

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    # id: 고유 번호 (자동 증가)
    # primary_key=True: 기본 키 (각 행을 구분하는 고유 값)
    # index=True: 빠른 검색을 위한 인덱스 생성
    # autoincrement=True: 1, 2, 3... 자동으로 증가

    user_id = Column(String(50), nullable=False, index=True)
    # user_id: 사용자 ID
    # String(100): 최대 100자
    # nullable=False: 필수 입력 (NULL 불가)
    # index=True: 사용자별 검색이 많으므로 인덱스 추가

    message = Column(Text, nullable=False)
    # message: 사용자가 입력한 메시지
    # Text: 긴 텍스트 저장 가능 (제한 없음)
    # nullable=False: 필수 입력

    response = Column(Text, nullable=False)
    # response: AI의 응답
    # Text: 긴 응답도 저장 가능

    filtered = Column(Boolean, default=False)
    # filtered: 보안 필터링 여부
    # Boolean: True/False
    # default=False: 기본값은 False (필터링 안 됨)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    # created_at: 생성 시간
    # DateTime: 날짜 + 시간
    # default=datetime.utcnow: 현재 시간 자동 입력
    # nullable=False: 필수 (자동으로 입력됨)


    # ========================================
    # 헬퍼 메서드
    # ========================================

    def __repr__(self):
        """
        객체를 문자열로 표현 (디버깅용)
        print(chat_log) 하면 이 형식으로 출력
        """
        return f"<ChatLog(id={self.id}, user={self.user_id}, filtered={self.filtered})>"


    def to_dict(self):
        """
        객체를 딕셔너리로 변환 (API 응답용)

        Returns:
            dict: 채팅 로그 정보
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "message": self.message,
            "response": self.response,
            "filtered": self.filtered,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ========================================
# 테스트 코드
# ========================================
if __name__ == "__main__":
    # 이 파일을 직접 실행하면 테이블 구조 출력
    print("=" * 50)
    print("[ChatLog 테이블 구조]")
    print("=" * 50)
    print(f"테이블 이름: {ChatLog.__tablename__}")
    print("\n컬럼 목록:")
    for column in ChatLog.__table__.columns:
        print(f"  - {column.name}: {column.type}")
    print("=" * 50)
