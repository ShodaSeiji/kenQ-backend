from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.mymodels import CompanyUser
from components.hash import verify_password
from schemas import UserLogin

router = APIRouter(
    prefix="/auth",
    tags=["認証"]
)

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(CompanyUser).filter_by(company_user_name=user.company_user_name).first()
    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=401, detail="認証に失敗しました")

    return {
        "id": db_user.company_user_id,
        "name": db_user.company_user_name,
        "company_id": db_user.company_id
    }