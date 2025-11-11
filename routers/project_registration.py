'''
案件情報を登録し、ベクトルサーチによるマッチングを行った結果を返すエンドポイントです。
'''

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from datetime import datetime, timedelta, timezone

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import ProjectInformation, MatchingInformation

# スキーマのインポート
from schemas import Project

# ベクトル検索用のモジュールインポート
from components.search_researchers import search_researchers

router = APIRouter(prefix="/project-registration", tags=["案件登録"])


'''
事業者の課題登録
'''
@router.post("")
def add_project(
    project_info: Project,
    db: Session = Depends(get_db)
    ):
    try:
        # 日本時間(UTS+9)
        JST = timezone(timedelta(hours=9))
        now_jst = datetime.now(JST)
        # print("受け取ったデータ:", project_info)

        # Step1: クエリ用のテキストを抽出（Projectモデルから）
        company_user_id = project_info.company_user_id
        project_title = project_info.project_title
        project_content = project_info.project_content
        industry_category = project_info.industry_category
        business_description = project_info.business_description
        university = ','.join(project_info.university) if project_info.university else ''
        preferred_researcher_level = ','.join(project_info.preferred_researcher_level) if project_info.preferred_researcher_level else ''

        # Step 2: DBに新しいプロジェクトを登録
        new_project = ProjectInformation(
            company_user_id = company_user_id,
            project_title = project_title,
            project_content = project_content,
            industry_category = industry_category,
            business_description = business_description,
            university = university,
            preferred_researcher_level = preferred_researcher_level,
            registration_date = now_jst
        )
        # print("プロジェクト登録前")
        db.add(new_project)
        db.commit()
        db.refresh(new_project)  # 登録後のIDなどを取得
        # print("プロジェクト登録完了")

        # Step 3: ベクトル検索実行（top_k件の研究者を取得）
        # 文字列を配列に変換してsearch_researchers関数に渡す
        university_list = university.split(',') if university else []
        preferred_researcher_level_list = preferred_researcher_level.split(',') if preferred_researcher_level else []
        
        search_results = search_researchers(
                title = project_title,
                description = project_content,
                industry = industry_category, #業種は現状フィルタリングに使わない
                business_description = business_description, #事業内容は現状フィルタリングに使わない
                preferred_researcher_level = preferred_researcher_level_list,
                university = university_list,
                top_k = 10
            )

        # Step 4: マッチング結果をDBに登録 & matching_idを取得
        matching_data = []
        for researcher in search_results:
            matching = MatchingInformation(
                project_id = new_project.project_id,
                researcher_id = researcher["researcher_id"],
                matching_reason = researcher["explanation"], 
                favorite_status = False,  # 初期値: お気に入りではない
            )
            db.add(matching)
            db.commit()  # 各レコードごとにコミットしてIDを取得
            db.refresh(matching)  # matching_idを取得
            
            # 研究者情報とmatching_idを組み合わせ
            researcher_with_matching = {
                "matching_id": matching.matching_id,
                "researcher_info": researcher,
                "favorite_status": False
            }
            matching_data.append(researcher_with_matching)

        # Step 5: 結果を返す
        return {
            "project_id": new_project.project_id,
            "project_title": project_title,
            "project_content": project_content,
            "industry_category": industry_category,
            "business_description": business_description,
            "university": university,
            "level" : preferred_researcher_level,
            "matched_researchers": search_results
        }

    except Exception as e:
        db.rollback()
        # print("例外発生！:", e)
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")