'''
researcher_idから研究者情報を取得するエンドポイント
'''

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from database.connection import get_db
from database.mymodels import ResearcherInformation

router = APIRouter(prefix="/researcher-info", tags=["研究者情報取得"])

@router.get("/{researcher_id}")
def get_researcher_by_id(
    researcher_id: int,
    db: Session = Depends(get_db)
):
    try:
        # researcher_idで研究者情報を取得
        stmt = select(ResearcherInformation).where(
            ResearcherInformation.researcher_id == researcher_id
        )
        researcher = db.execute(stmt).scalar_one_or_none()
        
        if not researcher:
            raise HTTPException(status_code=404, detail="研究者が見つかりません")
        
        # 研究者情報を返す
        return {
            "researcher_id": researcher.researcher_id,
            "researcher_name": researcher.researcher_name,
            "researcher_name_kana": researcher.researcher_name_kana,
            "researcher_name_alphabet": researcher.researcher_name_alphabet,
            "researcher_affiliation_current": researcher.researcher_affiliation_current,
            "researcher_department_current": researcher.researcher_department_current,
            "researcher_position_current": researcher.researcher_position_current,
            "researcher_affiliations_past": researcher.researcher_affiliations_past,
            "research_field_pi": researcher.research_field_pi,
            "keywords_pi": researcher.keywords_pi,
            "kaken_url": researcher.kaken_url
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")