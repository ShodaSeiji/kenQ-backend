'''
お気に入り登録機能のエンドポイントです。
'''
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

# スキーマのインポート
from schemas import FavoriteRequest

# DB操作用のモジュールインポート
from database.connection import get_db
from database.mymodels import MatchingInformation

router = APIRouter(prefix="/favorites", tags=["お気に入り登録"])

'''
matching_idを指定してfavorite_statusをtrue/falseに変更する
'''
@router.put("/{matching_id}")
def toggle_favorite(
    matching_id: int,
    request: FavoriteRequest,
    db: Session = Depends(get_db)
    ):
    try:
        # matching_idでレコードを検索
        matching_record = db.query(MatchingInformation).filter(
            MatchingInformation.matching_id == matching_id
        ).first()

        if not matching_record:
            raise HTTPException(
                status_code=404, 
                detail=f"該当するマッチング情報が見つかりません: matching_id={request.matching_id}"
            )

        # favorite_statusを更新
        matching_record.favorite_status = request.favorite_status
        db.commit()

        return {
            "message": "お気に入り状態を更新しました",
            "matching_id": request.matching_id,
            "favorite_status": request.favorite_status
        }

    except HTTPException:
        # HTTPExceptionは再発生させる
        raise
    except Exception as e:
        db.rollback()
        print("例外発生！:", e)
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")

'''
特定のmatching_idのお気に入り状態を取得する

@router.get("/{matching_id}")
def get_favorite_status(
    matching_id: int,
    db: Session = Depends(get_db)
    ):
    try:
        matching_record = db.query(MatchingInformation).filter(
            MatchingInformation.matching_id == matching_id
        ).first()

        if not matching_record:
            raise HTTPException(
                status_code=404, 
                detail=f"該当するマッチング情報が見つかりません: matching_id={matching_id}"
            )

        return {
            "matching_id": matching_id,
            "favorite_status": matching_record.favorite_status
        }

    except HTTPException:
        raise
    except Exception as e:
        print("例外発生！:", e)
        raise HTTPException(status_code=500, detail=f"サーバー内部エラー: {e}")
'''