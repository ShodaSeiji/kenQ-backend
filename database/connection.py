#データベースに接続
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# ローカルで動かす時用
from dotenv import load_dotenv
load_dotenv()

SERVER_URL=os.getenv("SERVER_URL")
DATABASE=os.getenv("DATABASE")
USER_NAME=os.getenv("USER_NAME")
PASSWORD=os.getenv("PASSWORD")
SERVER_PORT=os.getenv("SERVER_PORT")

DATABASE_URL = f"mysql+pymysql://{USER_NAME}:{PASSWORD}@{SERVER_URL}:{SERVER_PORT}/{DATABASE}?charset=utf8"

# データベースエンジンを作成
engine = create_engine(
    DATABASE_URL,
    connect_args={
        'ssl': {
            'ssl_disabled': False,
            'ssl_verify_cert': False,
            'ssl_verify_identity': False
        }
    },
    echo=False, 
    pool_pre_ping=True
)

# セッションファクトリを作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    # セッションを作成
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
