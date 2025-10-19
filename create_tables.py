from database.mymodels import Base
from database.connection import engine

# 全てのテーブルを作成
Base.metadata.create_all(bind=engine)
print("✅ テーブルが正常に作成されました！")
