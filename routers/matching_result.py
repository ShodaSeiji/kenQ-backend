'''
project_idからマッチングされた全ての研究者情報を取得するエンドポイント
'''

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List

from database.connection import get_db
from database.mymodels import MatchingInformation, ResearcherInformation, ProjectInformation

router = APIRouter(prefix="/matching-result", tags=["マッチング結果取得"])

@router.get("/{project_id}")
def get_matching_researchers(
    project_id: int,
    db: Session = Depends(get_db)
):
    try:
        # project_idに対応するマッチング情報、研究者情報、プロジェクト情報をJOINで取得
        stmt = select(
            MatchingInformation.matching_id,
            MatchingInformation.matching_reason,
            MatchingInformation.favorite_status,
            ResearcherInformation,
            ProjectInformation
        ).join(
            ResearcherInformation, 
            MatchingInformation.researcher_id == ResearcherInformation.researcher_id
        ).join(
            ProjectInformation,
            MatchingInformation.project_id == ProjectInformation.project_id
        ).where(
            MatchingInformation.project_id == project_id
        ).order_by(MatchingInformation.matching_id) # matching_idで昇順にソート（＝スコアが高い順）
        
        results = db.execute(stmt).fetchall()
        
        if not results:
            raise HTTPException(status_code=404, detail="該当するマッチング結果が見つかりません")
        
        # 結果を整形
        matching_results = []
        for row in results:
            researcher_data = {
                "matching_id": row.matching_id,
                "matching_reason": row.matching_reason,
                "favorite_status": row.favorite_status,
                "researcher_info": {
                    "researcher_id": row.ResearcherInformation.researcher_id,
                    "researcher_name": row.ResearcherInformation.researcher_name,
                    "researcher_name_kana": row.ResearcherInformation.researcher_name_kana,
                    "researcher_name_alphabet": row.ResearcherInformation.researcher_name_alphabet,
                    "researcher_affiliation_current": row.ResearcherInformation.researcher_affiliation_current,
                    "researcher_department_current": row.ResearcherInformation.researcher_department_current,
                    "researcher_position_current": row.ResearcherInformation.researcher_position_current,
                    "researcher_affiliations_past": row.ResearcherInformation.researcher_affiliations_past,
                    "research_field_pi": row.ResearcherInformation.research_field_pi,
                    "keywords_pi": row.ResearcherInformation.keywords_pi,
                    "kaken_url": row.ResearcherInformation.kaken_url
                }
            }
            matching_results.append(researcher_data)
        
        # 最初の結果からプロジェクト情報を取得（全て同じプロジェクトなので）
        project_info = results[0].ProjectInformation if results else None
        
        if not project_info:
            raise HTTPException(status_code=404, detail="プロジェクト情報が見つかりません")
        
        return {
            "project_id": project_id,
            "project_title": project_info.project_title,
            "project_content": project_info.project_content,
            "industry_category": project_info.industry_category,
            "business_description": project_info.business_description,
            "university": project_info.university,
            "preferred_researcher_level": project_info.preferred_researcher_level,
            "matched_researchers": matching_results,
            "total_count": len(matching_results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")