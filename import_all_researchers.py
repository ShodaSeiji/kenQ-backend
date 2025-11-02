from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from database.connection import get_db
from database.mymodels import ResearcherInformation
import os
from dotenv import load_dotenv

load_dotenv()

search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name=os.getenv("AZURE_SEARCH_INDEX_NAME"),
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

db = next(get_db())

def truncate_text(text, max_length=255):
    if not text:
        return ""
    return text[:max_length] if len(text) > max_length else text

try:
    # ページングで全データを取得
    skip = 0
    page_size = 1000
    total_count = 0
    
    while True:
        results = list(search_client.search(
            search_text="*",
            select=["researcher_id", "name", "university", "affiliation", "position", "research_field", "keywords"],
            top=page_size,
            skip=skip
        ))
        
        if not results:
            break
            
        for result in results:
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
                total_count += 1
                
                if total_count % 100 == 0:
                    db.commit()
                    print(f"進行中... {total_count}件")
        
        skip += page_size
        
        if len(results) < page_size:
            break
    
    db.commit()
    print(f"✅ {total_count}件の研究者データをインポートしました")
    print(f"総データ数: {db.query(ResearcherInformation).count()}件")
    
except Exception as e:
    print(f"❌ エラー: {e}")
    db.rollback()
finally:
    db.close()
