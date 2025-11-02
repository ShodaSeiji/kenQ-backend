from database.connection import get_db
from database.mymodels import ResearcherInformation

db = next(get_db())

try:
    # 全研究者数を確認
    total = db.query(ResearcherInformation).count()
    print(f"研究者データ総数: {total}件")
    
    # 特定のIDを確認
    target_id = 20345367
    researcher = db.query(ResearcherInformation).filter_by(researcher_id=target_id).first()
    
    if researcher:
        print(f"\n✅ researcher_id={target_id} が見つかりました")
        print(f"名前: {researcher.researcher_name}")
    else:
        print(f"\n❌ researcher_id={target_id} が見つかりません")
        
        # サンプルデータを表示
        print("\n登録されている研究者IDのサンプル:")
        samples = db.query(ResearcherInformation).limit(10).all()
        for s in samples:
            print(f"  - ID: {s.researcher_id}, 名前: {s.researcher_name}")
    
except Exception as e:
    print(f"❌ エラー: {e}")
finally:
    db.close()
