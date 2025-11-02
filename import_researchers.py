from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from database.connection import get_db
from database.mymodels import ResearcherInformation
import os
from dotenv import load_dotenv

load_dotenv()

# Azure AI Search クライアント
search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

db = next(get_db())

def truncate_text(text, max_length=255):
    """テキストを指定の長さに切り詰める"""
    if not text:
        return ""
    return text[:max_length] if len(text) > max_length else text

try:
    # Azure AI Searchから全研究者を取得
    results = search_client.search(
        search_text="*",
        select=["researcher_id", "name", "university", "affiliation", "position", "research_field", "keywords"],
        top=1000
    )
    
    count = 0
    for result in results:
        # 既に存在するか確認
        existing = db.query(ResearcherInformation).filter_by(
            researcher_id=int(result["researcher_id"])
        ).first()
        
        if not existing:
            researcher = ResearcherInformation(
                researcher_id=int(result["researcher_id"]),
                researcher_name=truncate_text(result.get("name", ""), 255),
                researcher_name_kana="",
                researcher_name_alphabet="",
                researcher_affiliation_current=truncate_text(result.get("university", ""), 255),
                researcher_department_current=truncate_text(result.get("affiliation", ""), 255),
                researcher_position_current=truncate_text(result.get("position", ""), 255),
                researcher_affiliations_past="",
                research_field_pi=truncate_text(result.get("research_field", ""), 255),
                keywords_pi=truncate_text(result.get("keywords", ""), 255),
                kaken_url=""
            )
            db.add(researcher)
            count += 1
            
            # 100件ごとにコミット
            if count % 100 == 0:
                db.commit()
                print(f"進行中... {count}件")
    
    db.commit()
    print(f"✅ {count}件の研究者データをインポートしました")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    db.rollback()
finally:
    db.close()
