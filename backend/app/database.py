"""
데이터베이스 연결 및 세션 관리

이 파일이 하는 일:
1. DB 엔진 생성 (SQLite/PostgreSQL 연결)
2. 테이블 생성 (models/chat_log.py의 설계도 사용)
3. 세션 팩토리 제공 (다른 파일에서 DB 사용할 수 있게)
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from app.utils.config import settings
from app.models.chat_log import Base


# ========================================
# 비동기 엔진 생성 (aiosqlite 사용)
# ========================================
engine = create_async_engine(
    settings.DATABASE_URL,
    # SQLite 설정
    echo=settings.DEBUG,  # SQL 쿼리 로그 출력 (개발 시 True)
    future=True,          # SQLAlchemy 2.0 스타일 사용
)

# ========================================
# 비동기 세션 팩토리
# ========================================
AsyncSessionLocal = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,  # commit 후에도 객체 사용 가능
)


# ========================================
# 의존성 주입용 함수 (FastAPI에서 사용)
# ========================================
async def get_db():
    """
    FastAPI 의존성 주입용 DB 세션 제공

    사용 예:
    @app.get("/logs")
    async def get_logs(db: AsyncSession = Depends(get_db)):
        logs = await db.execute(select(ChatLog))
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session  # FastAPI에 세션 제공
        finally:
            await session.close()


# ========================================
# 테이블 생성 함수
# ========================================
async def init_db():
    """
    데이터베이스 초기화 및 테이블 생성

    서버 시작 시 main.py에서 호출됩니다.
    """
    async with engine.begin() as conn:
        # Base.metadata에 등록된 모든 테이블 생성
        # (현재는 ChatLog만 있음)
        await conn.run_sync(Base.metadata.create_all)

    print("[OK] 데이터베이스 초기화 완료!")
    print(f"   - DB: {settings.DATABASE_URL}")


# ========================================
# 테이블 삭제 함수 (개발용)
# ========================================
async def drop_db():
    """
    모든 테이블 삭제 (주의: 개발 환경에서만 사용!)

    운영 환경에서는 절대 사용하지 마세요!
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    print("[WARNING] 모든 테이블이 삭제되었습니다!")


# ========================================
# 테스트 함수 (직접 실행 시)
# ========================================
async def test_connection():
    """DB 연결 테스트"""
    try:
        # 테이블 생성
        await init_db()

        # 테스트 데이터 삽입
        from app.models.chat_log import ChatLog
        from datetime import datetime

        async with AsyncSessionLocal() as session:
            # 테스트 로그 생성
            test_log = ChatLog(
                user_id="test_user",
                message="테스트 메시지",
                response="테스트 응답",
                filtered=False
            )

            session.add(test_log)
            await session.commit()
            await session.refresh(test_log)

            print(f"[OK] 테스트 데이터 저장 성공! ID: {test_log.id}")

            # 데이터 조회
            from sqlalchemy import select
            result = await session.execute(select(ChatLog))
            logs = result.scalars().all()

            print(f"[OK] 저장된 로그 수: {len(logs)}")
            for log in logs:
                print(f"   - {log}")

    except Exception as e:
        print(f"[ERROR] 에러 발생: {e}")
        import traceback
        traceback.print_exc()


# ========================================
# 직접 실행 시 테스트
# ========================================
if __name__ == "__main__":
    import asyncio

    print("=" * 50)
    print("[데이터베이스 연결 테스트]")
    print("=" * 50)

    # 비동기 함수 실행
    asyncio.run(test_connection())

    print("=" * 50)
