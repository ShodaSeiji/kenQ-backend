'''
リクエストボディに使うスキーマを定義するファイルです。
'''

from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# 案件情報登録用
class Project(BaseModel):
    company_user_id: int
    project_title: str
    project_content: str
    industry_category: str 
    business_description: str 
    university: Optional[List[str]] = None # 複数の大学名に対応
    preferred_researcher_level: Optional[List[str]] = None # 複数の職位に対応


# お気に入り登録用
class FavoriteRequest(BaseModel):
    matching_id: int
    favorite_status: bool

# 認証用
class UserLogin(BaseModel):
    company_user_name: str
    password: str

# AI課題診断用
class AIDiagnosisRequest(BaseModel):
    industry_category: str
    business_description: str
    project_content: str