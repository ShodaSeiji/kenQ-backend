from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB操作用のモジュールインポート
from database.connection import get_db

# ルータのインポート
from routers import add_to_favorites, project_registration, ai_diagnosis, auth, researcher_info, matching_result, project_info, researchers_en

import os
from dotenv import load_dotenv
load_dotenv()

ALLOWED_ORIGINS=os.getenv("ALLOWED_ORIGINS")


# インスタンス化
app = FastAPI(
    title="研Q MVP",
    description="研Q MVPのAPI",
    version="0.0.0"
)

# ルータ登録
app.include_router(project_registration.router) #プロジェクト登録(PJ登録～ベクトルサーチ結果登録)
app.include_router(add_to_favorites.router) #お気に入り登録機能
app.include_router(ai_diagnosis.router) #AI課題診断用
app.include_router(auth.router) # 認証用
app.include_router(researcher_info.router) # 研究者情報取得用（※不要かも）
app.include_router(matching_result.router) # マッチング結果取得用
app.include_router(project_info.router) # マイページ案件一覧取得用
app.include_router(researchers_en.router) # 英語研究者情報取得用

# CORS設定.開発中はとりあえず全てのメソッド、ヘッダーを許可.オリジンはローカル/本番を併記
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGINS, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)