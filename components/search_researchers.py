# キーワードのみでベクトル化したインデックスを使用したベクトル検索用

import os
import pandas as pd
import openai
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.models import VectorizedQuery
from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    VectorSearch, HnswAlgorithmConfiguration, HnswParameters, VectorSearchProfile
)
import requests
import json

# ローカルで動かす時用
from dotenv import load_dotenv

load_dotenv()


# 環境変数からAzureのAPIキーを取得
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_GPT_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_GPT_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")

# OpenAI API クライアント設定
openai.api_key = AZURE_OPENAI_API_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_version = "2023-07-01-preview"

# Azure AI Search クライアント設定
search_client = SearchClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    index_name=AZURE_SEARCH_INDEX_NAME,
    credential=AzureKeyCredential(AZURE_SEARCH_API_KEY)
)

# 埋め込みを取得する関数
def get_embedding(text):
    response = openai.embeddings.create(
        input=text,
        model=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME")
    )
    return response.data[0].embedding

# 依頼に基づく研究者検索
def search_researchers(title, description, industry, business_description, preferred_researcher_level, university, top_k=10):
    try:
        query_text = f" {title} {description}"
        embedding = get_embedding(query_text)

        # フィルタ条件を生成：教員職位と大学
        filter_conditions = []

        if university and not ("全大学" in university):
            university_filters = [f"university eq '{u}'" for u in university]
            filter_conditions.append(f"({' or '.join(university_filters)})")

        if preferred_researcher_level:
            position_filters = [f"position eq '{p}'" for p in preferred_researcher_level]
            filter_conditions.append(f"({' or '.join(position_filters)})")
        
        filter_expression = " and ".join(filter_conditions) if filter_conditions else None

        results = search_client.search(
            search_text=None,
            vector_queries=[
                VectorizedQuery(
                    vector=embedding,
                    k_nearest_neighbors=top_k,
                    fields="vector"
                )
            ],
            select=["researcher_id", "name", "university", "affiliation", "position","research_field", "keywords"],
            filter=filter_expression
        )

        search_results = []
        for result in results:
            explanation = generate_explanation(query_text, result)
            search_results.append({
                "researcher_id": result["researcher_id"],
                "name": result["name"],
                "university": result["university"],
                "affiliation": result["affiliation"],
                "position": result["position"],
                "research_field": result["research_field"],
                "keywords": result["keywords"],
                "explanation": explanation
            })
        
        return search_results
    
    except Exception as e:
        print("search_researchers内で例外発生:", e)
        raise

def get_openai_response(messages):
    """
    Azure OpenAI Serviceにチャットメッセージを送信し、応答を取得する関数。

    Parameters:
    messages (list): チャットメッセージのリスト。各メッセージは辞書で、'role'と'content'を含む。

    Returns:
    str: アシスタントからの応答メッセージ。
    """
    # 環境変数からAPIキーとエンドポイントを取得
    api_key = os.getenv("AZURE_OPENAI_GPT_API_KEY")
    api_base = os.getenv("AZURE_OPENAI_GPT_ENDPOINT")
    deployment_name = os.getenv("AZURE_OPENAI_GPT_DEPLOYMENT_NAME")  # デプロイメント名を環境変数から取得

    # エンドポイントURLの構築
    api_version = "2024-08-01-preview"  # 使用するAPIバージョンを指定
    endpoint = f"{api_base}/openai/deployments/{deployment_name}/chat/completions?api-version={api_version}"

    # ヘッダーの設定
    headers = {
        "Content-Type": "application/json",
        "api-key": api_key
    }

    # リクエストデータの作成
    data = {
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 300
    }

    # POSTリクエストの送信
    response = requests.post(endpoint, headers=headers, data=json.dumps(data))

    # レスポンスの処理
    if response.status_code == 200:
        response_data = response.json()
        return response_data['choices'][0]['message']['content']
    else:
        raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


# 研究者のマッチ理由を生成
def generate_explanation(query_text, researcher):
    prompt = f"""
    依頼内容: {query_text}
    研究者: {researcher["name"]}
    大学: {researcher["university"]}
    所属: {researcher["affiliation"]}
    研究分野： {researcher["research_field"]}
    キーワード： {researcher["keywords"]}

    なぜこの研究者が依頼内容に適しているのかを簡潔に説明してください。
    """
    messages=[{"role": "system", "content": "あなたは検索結果の解説を行うアシスタントです。"},
            {"role": "user", "content": prompt}]

    return get_openai_response(messages)
