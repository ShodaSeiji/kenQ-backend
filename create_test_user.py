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

    # ユーザー1を作成
    password1 = "testaco"
    hashed1 = bcrypt.hashpw(password1.encode('utf-8'), bcrypt.gensalt())

    # 既存のユーザーをチェック
    existing_user1 = db.query(CompanyUser).filter(CompanyUser.company_user_name == "test").first()
    if existing_user1:
        print(f"⚠️ ユーザー 'test' は既に存在します。スキップします。")
    else:
        test_user1 = CompanyUser(
            company_id=company_id,
            company_user_name="test",
            password=hashed1.decode('utf-8')
        )
        db.add(test_user1)
        print(f"✅ ユーザー 'test' を作成しました")

    # ユーザー2を作成
    password2 = "testaco2"
    hashed2 = bcrypt.hashpw(password2.encode('utf-8'), bcrypt.gensalt())

    existing_user2 = db.query(CompanyUser).filter(CompanyUser.company_user_name == "test2").first()
    if existing_user2:
        print(f"⚠️ ユーザー 'test2' は既に存在します。スキップします。")
    else:
        test_user2 = CompanyUser(
            company_id=company_id,
            company_user_name="test2",
            password=hashed2.decode('utf-8')
        )
        db.add(test_user2)
        print(f"✅ ユーザー 'test2' を作成しました")

    db.commit()

    print(f"\n✅ テストユーザーを作成しました")
    print(f"\nユーザー1:")
    print(f"  company_user_id: 1")
    print(f"  company_user_name: test")
    print(f"  password: testaco")
    print(f"\nユーザー2:")
    print(f"  company_user_id: 2")
    print(f"  company_user_name: test2")
    print(f"  password: testaco2")
    print(f"\nこの情報でログインしてください")

except Exception as e:
    print(f"❌ エラー: {e}")
    db.rollback()
finally:
    db.close()
