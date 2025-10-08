# kenQ Backend Deployment Guide

## Azure App Service へのデプロイ設定

このリポジトリは GitHub Actions を使用して Azure App Service に自動デプロイされます。

### デプロイ先情報

- **リソースグループ**: kenq-project-freePoC
- **App Service 名**: app-kenq-freepoc-3
- **デプロイ先URL**: https://app-kenq-freepoc-3-aqhzavcsf3gsgghs.japaneast-01.azurewebsites.net
- **デプロイブランチ**: master

### GitHub Secrets の設定

以下のシークレットが必要です：

1. **Publish Profile の取得**
   - Azure Portal > App Service "app-kenq-freepoc-3" > デプロイメント > デプロイセンター
   - 「プロファイルのダウンロード」をクリック
   - `.PublishSettings` ファイルをダウンロード

2. **GitHub Secrets への追加**
   - GitHub リポジトリ > Settings > Secrets and variables > Actions
   - New repository secret をクリック
   - 以下のシークレットを追加：
     - Name: `AZURE_WEBAPP_PUBLISH_PROFILE`
     - Value: ダウンロードした `.PublishSettings` ファイルの内容をペースト

### 環境変数の設定

Azure Portal > App Service "app-kenq-freepoc-3" > 設定 > 構成 で以下を設定：

- `SERVER_URL`: データベースサーバーURL
- `USER_NAME`: データベースユーザー名
- `PASSWORD`: データベースパスワード
- `DATABASE`: データベース名
- `SERVER_PORT`: 3306
- `SSL_CA_PATH`: DigiCertGlobalRootCA.crt.pem
- `AZURE_OPENAI_API_KEY`: Azure OpenAI APIキー
- `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`: Embeddingデプロイ名
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI エンドポイント
- `AZURE_OPENAI_GPT_API_KEY`: GPT APIキー
- `AZURE_OPENAI_GPT_DEPLOYMENT_NAME`: GPTデプロイ名
- `AZURE_OPENAI_GPT_ENDPOINT`: GPT エンドポイント
- `AZURE_SEARCH_API_KEY`: Azure Search APIキー
- `AZURE_SEARCH_ENDPOINT`: Azure Search エンドポイント
- `AZURE_SEARCH_INDEX_NAME`: インデックス名
- `ALLOWED_ORIGINS`: https://app-kenq-freepoc-4-h9ahafbpb6aqa3d9.japaneast-01.azurewebsites.net

### スタートアップコマンドの設定

Azure Portal > App Service > 設定 > 構成 > 全般設定

- スタートアップコマンド: `gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app`

### デプロイフロー

1. `master` ブランチに push すると自動的にデプロイが開始されます
2. GitHub Actions が以下を実行：
   - Python 3.11 のセットアップ
   - 依存関係のインストール
   - アプリケーションのビルド
   - Azure App Service へのデプロイ

### 手動デプロイ

GitHub リポジトリの Actions タブから「Build and deploy Python app to Azure Web App - app-kenq-freepoc-3」ワークフローを選択し、「Run workflow」をクリックすることで手動デプロイも可能です。

### トラブルシューティング

- デプロイログは GitHub Actions の Logs で確認できます
- アプリケーションログは Azure Portal > App Service > 監視 > ログストリーム で確認できます
