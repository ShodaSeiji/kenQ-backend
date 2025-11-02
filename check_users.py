from database.connection import get_db
from database.mymodels import CompanyUser, Company

db = next(get_db())

print("=== 企業一覧 ===")
companies = db.query(Company).all()
for company in companies:
    print(f"ID: {company.company_id}, 名前: {company.company_name}")

print("\n=== 企業ユーザー一覧 ===")
users = db.query(CompanyUser).all()
if users:
    for user in users:
        print(f"ID: {user.company_user_id}, ユーザー名: {user.company_user_name}, 企業ID: {user.company_id}")
else:
    print("ユーザーが登録されていません")

db.close()
