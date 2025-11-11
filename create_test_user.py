from database.connection import get_db
from database.mymodels import CompanyUser, Company
import bcrypt

db = next(get_db())

try:
    # 既存の企業をチェック
    existing_company = db.query(Company).first()
    
    if not existing_company:
        # 企業を作成
        test_company = Company(company_name="テスト企業")
        db.add(test_company)
        db.commit()
        db.refresh(test_company)
        company_id = test_company.company_id
        print("✅ テスト企業を作成しました")
    else:
        company_id = existing_company.company_id
        print(f"✅ 既存の企業を使用します: {existing_company.company_name}")
    
    # パスワードをハッシュ化
    password = "test1234"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # ユーザーを作成
    test_user = CompanyUser(
        company_id=company_id,
        company_user_name="testuser",
        password=hashed.decode('utf-8')
    )
    db.add(test_user)
    db.commit()
    
    print(f"\n✅ テストユーザーを作成しました")
    print(f"ユーザー名: testuser")
    print(f"パスワード: test1234")
    print(f"\nこの情報でログインしてください")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    db.rollback()
finally:
    db.close()
