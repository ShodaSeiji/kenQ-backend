import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import engine
from database.mymodels import Base

# テーブル作成
if __name__ == "__main__":
    try:
        Base.metadata.create_all(bind=engine)
        print("✅ テーブル作成が完了しました")
    except Exception as e:
        print(f"❌ テーブル作成時にエラーが発生しました: {e}")