from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# SQLite 데이터베이스 경로
DATABASE_URL = "sqlite:///./ktb_web3.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI 의 Depends 에서 사용할 세션 의존성.
    요청마다 DB 세션을 열고, 응답 후 닫는다.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

