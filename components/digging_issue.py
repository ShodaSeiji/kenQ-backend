import os
import requests
import json
from openai import OpenAI

# ローカルで動かす時用
from dotenv import load_dotenv

load_dotenv()

# search_researchers.pyにも同様のモジュールがあるためまとめた方がよいかも。
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
      "max_tokens": 1000
   }

   # POSTリクエストの送信
   response = requests.post(endpoint, headers=headers, data=json.dumps(data))

   # レスポンスの処理
   if response.status_code == 200:
      response_data = response.json()
      return response_data['choices'][0]['message']['content']
   else:
      raise Exception(f"Request failed with status code {response.status_code}: {response.text}")


# LLMを用いて課題の深堀
def digging_issue(industry: str, business: str, challenge: str, language: str = "ja") -> str:
   # 言語に応じたプロンプトの選択
   if language == "en":
      prompt = f"""
      The following three variables are input from the user:

      - Industry classification (industry): {industry}
      - Business description (business): {business}
      - Business challenge (challenge): {challenge}

      Based on the above input information, please output a condensed information text containing the following four elements to achieve high similarity in subsequent vector searches.

      [Elements to Output]
      1. Challenge Overview
      Focusing on the content of {challenge}, briefly describe the background, objectives, industry-specific challenges, specific needs related to {business}, problems to be solved, and expected outcomes.

      2. Extracted Keywords and Concepts
      List representative technical terms, business terms, related concepts, and specific approaches (e.g., AI, IoT, data analysis, sustainability, optimization, simulation, etc.) related to {industry} and {business}.

      3. Applicable Research Fields and Technical Approaches
      Describe what academic fields, research methods, and technical approaches can contribute to {challenge}. Include past case studies and applicable research areas.

      4. Collaboration Possibilities and Synergies
      Describe the synergistic effects obtained through collaboration with researchers, feasible application scenarios, and constraints or prerequisites to be considered in advance.

      [Writing Notes]

      - Clearly write out each element as keywords or concepts that are effective for vectorization.
      - To supplement the abstractness of {challenge}, appropriately add related hypotheses or associations with other fields.
      - Include information from both business and research perspectives in a balanced manner and create a consistent structure.

      [Output Format Example]
      "[Challenge Overview]... [Keywords]... [Research Fields/Technical Approaches]... [Collaboration/Synergy]..."

      Following this template, generate a sentence suitable for vectorization using {industry}, {business}, and {challenge} as input variables.
      """
      system_message = "You are an assistant that creates information texts for a system that matches business challenges with researchers' research content."
   else:
      prompt = f"""
      以下の3つの変数がユーザーから入力されます：

      - 産業分類（industry）：{industry}
      - 事業内容（business）：{business}
      - 事業の課題（challenge）：{challenge}

      上記の入力情報を基に、後続のベクトルサーチで高い類似度が得られるよう、以下の4つの要素を含む濃縮された情報文章を出力してください。

      【出力すべき要素】
      1. 課題概要
      {challenge} の内容を中心に、背景、目的、業界特有の課題、{business} に関連する具体的なニーズ、解決すべき問題点や期待される成果を簡潔に記述してください。

      2. 抽出したキーワード・コンセプト
      {industry} や {business} に関する代表的な技術用語、ビジネス用語、関連概念、具体的なアプローチ（例：AI、IoT、データ解析、サステナビリティ、最適化、シミュレーションなど）を列挙してください。

      3. 対応可能な研究分野や技術アプローチ
      {challenge} に対して、どのような学術分野・研究手法・技術的アプローチが貢献可能かを記述してください。過去の事例や応用可能な研究領域も含めてください。

      4. 連携の可能性とシナジー
      研究者との連携によって得られる相乗効果、実現可能な応用シナリオ、事前に考慮すべき制約条件や前提条件を含めて記述してください。

      【文章作成の注意点】

      - 各要素はベクトル化に有効なキーワードや概念として明確に書き出してください。
      - {challenge} の抽象性を補完するために、関連する仮説や他分野との関連付けを適宜加えてください。
      - ビジネス視点と研究視点の両方からの情報をバランスよく含め、一貫性ある構成にしてください。

      【出力フォーマット例】
      「【課題概要】... 【キーワード】... 【研究分野・技術アプローチ】... 【連携・シナジー】...」

      このテンプレートに従い、{industry}、{business}、{challenge} を入力変数としてベクトル化に適した文章を生成してください。
      """
      system_message = "あなたは、事業会社の課題と研究者の研究内容をマッチングするシステムのための情報文章を作成するアシスタントです。"

   messages=[
      {"role": "system", "content": system_message},
      {"role": "user", "content": prompt}
   ]
   return get_openai_response(messages)
