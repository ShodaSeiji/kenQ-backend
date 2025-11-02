from database.connection import get_db
from database.mymodels import CompanyUser
from components.hash import verify_password
import bcrypt

db = next(get_db())

# ユーザーを取得
user = db.query(CompanyUser).filter_by(company_user_name="testuser").first()

if user:
    print(f"✅ ユーザーが見つかりました")
    print(f"ユーザー名: {user.company_user_name}")
    print(f"ハッシュ化されたパスワード: {user.password[:50]}...")
    
    # パスワード検証をテスト
    test_password = "test1234"
    
    # 方法1: verify_password関数を使用
    try:
        result1 = verify_password(test_password, user.password)
        print(f"\nverify_password関数の結果: {result1}")
    except Exception as e:
        print(f"\nverify_password関数エラー: {e}")
    
    # 方法2: bcryptを直接使用
    try:
        result2 = bcrypt.checkpw(test_password.encode('utf-8'), user.password.encode('utf-8'))
        print(f"bcrypt.checkpw の結果: {result2}")
    except Exception as e:
        print(f"bcrypt.checkpw エラー: {e}")
        
else:
    print("❌ ユーザーが見つかりません")

db.close()
