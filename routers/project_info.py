'''
company_idから登録した案件一覧を取得するエンドポイント
'''

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select, func
from typing import List

from database.connection import get_db
from database.mymodels import CompanyUser, ProjectInformation, MatchingInformation

router = APIRouter(prefix="/project-info", tags=["マイページ用案件一覧取得"])

@router.get("/{company_id}")
def get_projects_by_company(
    company_id: str,
    db: Session = Depends(get_db)
):
    try:
        # company_idに対応するcompany_user_idとcompany_user_nameを取得
        stmt_users = select(CompanyUser.company_user_id, CompanyUser.company_user_name).where(CompanyUser.company_id == company_id)
        user_results = db.execute(stmt_users).fetchall()
        
        if not user_results:
            raise HTTPException(status_code=404, detail="該当する会社IDのユーザーが見つかりません")
        
        # 取得したcompany_user_idに対応する案件情報を取得
        user_ids = [row.company_user_id for row in user_results]
        user_name_map = {row.company_user_id: row.company_user_name for row in user_results}
        stmt_projects = select(ProjectInformation).where(ProjectInformation.company_user_id.in_(user_ids))
        project_results = db.execute(stmt_projects).scalars().all()
        
        if not project_results:
            raise HTTPException(status_code=404, detail="該当する案件情報が見つかりません")
        
        # 結果を整形
        projects_list = []
        for project in project_results:
            # お気に入り数をカウント
            favorite_count_stmt = select(func.count(MatchingInformation.matching_id)).where(
                MatchingInformation.project_id == project.project_id,
                MatchingInformation.favorite_status == True
            )
            favorite_count = db.execute(favorite_count_stmt).scalar()
            
            project_data = {
                "project_id": project.project_id,
                "company_user_id": project.company_user_id,
                "company_user_name": user_name_map.get(project.company_user_id),
                "project_title": project.project_title,
                "project_content": project.project_content,
                "industry_category": project.industry_category,
                "business_description": project.business_description,
                "university": project.university.split(',') if project.university else [],
                "preferred_researcher_level": project.preferred_researcher_level.split(',') if project.preferred_researcher_level else [],
                "registration_date": project.registration_date.isoformat(),
                "favorite_count": favorite_count or 0
            }
            projects_list.append(project_data)
        
        return {"projects": projects_list}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


"""

#プロジェクトIDから単一のプロジェクト情報を取得するエンドポイント（今回は不要？）
@router.get("/single/{project_id}")
def get_single_project_info(
    project_id: int,
    db: Session = Depends(get_db)
):
    try:
        # プロジェクト情報を取得
        project_stmt = select(ProjectInformation).where(
            ProjectInformation.project_id == project_id
        )
        project = db.execute(project_stmt).scalar_one_or_none()
        
        if not project:
            raise HTTPException(status_code=404, detail="プロジェクトが見つかりません")
        
        # お気に入り数をカウント
        favorite_count_stmt = select(func.count(MatchingInformation.matching_id)).where(
            MatchingInformation.project_id == project_id,
            MatchingInformation.favorite_status == True
        )
        favorite_count = db.execute(favorite_count_stmt).scalar()
        
        return {
            "project_id": project.project_id,
            "company_user_id": project.company_user_id,
            "project_title": project.project_title,
            "project_content": project.project_content,
            "industry_category": project.industry_category,
            "business_description": project.business_description,
            "university": project.university,
            "preferred_researcher_level": project.preferred_researcher_level,
            "registration_date": project.registration_date.isoformat(),
            "favorite_count": favorite_count or 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")

"""