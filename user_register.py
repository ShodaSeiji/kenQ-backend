import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import bcrypt
from database.connection import get_db
from database.mymodels import CompanyUser
from sqlalchemy.orm import Session

def hash_password(password: str) -> str:
    """パスワードをbcryptでハッシュ化する"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def register_company_user(company_id: int, company_user_name: str, password: str):
    """
    企業ユーザーをデータベースに登録する関数
    
    Parameters:
    company_id (int): 企業ID
    company_user_name (str): 企業ユーザー名
    password (str): パスワード（平文）
    
    Returns:
    dict: 登録結果
    """
    # データベースセッション取得
    db = next(get_db())
    
    try:
        # パスワードをハッシュ化
        hashed_password = hash_password(password)
        
        # ユーザー名の重複チェック
        existing_user = db.query(CompanyUser).filter(
            CompanyUser.company_user_name == company_user_name
        ).first()
        
        if existing_user:
            return {
                "success": False,
                "message": "このユーザー名は既に使用されています"
            }
        
        # 新しいユーザーを作成
        new_user = CompanyUser(
            company_id=company_id,
            company_user_name=company_user_name,
            password=hashed_password
        )
        
        # データベースに追加
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {
            "success": True,
            "message": "ユーザー登録が完了しました",
            "user_id": new_user.company_user_id,
            "company_user_name": new_user.company_user_name
        }
        
    except Exception as e:
        db.rollback()
        return {
            "success": False,
            "message": f"登録中にエラーが発生しました: {str(e)}"
        }
        
    finally:
        db.close()

if __name__ == "__main__":
    # テスト用のユーザー登録
    result = register_company_user(
        company_id=1,
        company_user_name="test2",
        password="testaco2"
    )
    
    print("登録結果:")
    print(f"成功: {result['success']}")
    print(f"メッセージ: {result['message']}")
    
    if result['success']:
        print(f"ユーザーID: {result['user_id']}")
        print(f"ユーザー名: {result['company_user_name']}")

"""
company_user_name="test",
password="testaco"

company_user_name="test2",
password="testaco2"
"""