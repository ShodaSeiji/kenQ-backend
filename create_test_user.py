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

    # 既存のテストユーザーを削除
    existing_users = db.query(CompanyUser).filter(
        CompanyUser.company_user_name.in_(["test", "test2"])
    ).all()

    for user in existing_users:
        db.delete(user)
        print(f"🗑️ 既存ユーザー '{user.company_user_name}' を削除しました")

    db.commit()

    # 新しいユーザーを作成
    users_to_create = [
        {"company_user_name": "test", "password": "testaco"},
        {"company_user_name": "test2", "password": "testaco2"}
    ]

    for user_data in users_to_create:
        # パスワードをハッシュ化
        hashed = bcrypt.hashpw(user_data["password"].encode('utf-8'), bcrypt.gensalt())

        # ユーザーを作成
        new_user = CompanyUser(
            company_id=company_id,
            company_user_name=user_data["company_user_name"],
            password=hashed.decode('utf-8')
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        print(f"\n✅ ユーザーを作成しました")
        print(f"   ID: {new_user.company_user_id}")
        print(f"   ユーザー名: {user_data['company_user_name']}")
        print(f"   パスワード: {user_data['password']}")

    print(f"\n✅ すべてのテストユーザーを作成しました")
    print(f"\n以下の情報でログインしてください:")
    print(f"━━━━━━━━━━━━━━━━━━━━")
    print(f"ユーザー1:")
    print(f"  ユーザー名: test")
    print(f"  パスワード: testaco")
    print(f"\nユーザー2:")
    print(f"  ユーザー名: test2")
    print(f"  パスワード: testaco2")
    print(f"━━━━━━━━━━━━━━━━━━━━")

except Exception as e:
    print(f"❌ エラー: {e}")
    db.rollback()
finally:
    db.close()
