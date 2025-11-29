# Vercel手動デプロイ手順

**作成日**: 2025年11月27日  
**目的**: Google Analytics設定を反映するためのVercel手動デプロイ手順

---

## 方法1: Vercel CLIを使用（推奨）

### ステップ1: Vercel CLIにログイン

```bash
cd /Users/kurinobu/projects/yadopera
vercel login
```

ブラウザが開き、Vercelアカウントでログインします。

### ステップ2: プロジェクトをリンク（初回のみ）

```bash
cd landing
vercel link
```

以下の質問に答えます：
- Set up and deploy? **Yes**
- Which scope? **個人アカウントを選択**
- Link to existing project? **Yes**
- What's the name of your existing project? **yadopera-landing**

### ステップ3: 本番環境にデプロイ

```bash
vercel --prod
```

これで最新のコミット（`4eddb00`）がデプロイされます。

---

## 方法2: Vercelダッシュボードから手動デプロイ

### ステップ1: Vercelダッシュボードにアクセス

1. https://vercel.com/dashboard にアクセス
2. プロジェクト「yadopera-landing」を選択

### ステップ2: GitHubリポジトリから直接デプロイ

1. 「Deployments」タブを開く
2. 「Create Deployment」ボタンをクリック（または「Import Project」）
3. GitHubリポジトリを選択: `kurinobu/yadopera`
4. ブランチ: `main` を選択
5. Root Directory: `landing` を指定
6. 「Deploy」をクリック

### ステップ3: デプロイ完了を待つ

デプロイが完了するまで1-2分待ちます。

---

## 方法3: GitHubのWebhookを手動でトリガー

### ステップ1: GitHubリポジトリにアクセス

1. https://github.com/kurinobu/yadopera にアクセス
2. Settings → Webhooks を開く

### ステップ2: VercelのWebhookを確認

1. VercelのWebhookが存在するか確認
2. 「Recent Deliveries」を確認
3. 最新の配信が成功しているか確認

### ステップ3: Webhookを手動で再送信

1. 最新の配信を選択
2. 「Redeliver」をクリック

---

## デプロイ後の確認

### 1. Vercelダッシュボードで確認

- 最新のデプロイが完了しているか
- コミット: `4eddb00` または `46a7aba` が含まれているか
- ステータス: 「Ready」

### 2. ブラウザで確認

1. `https://yadopera.com` にアクセス
2. ページのソースを表示（右クリック → 「ページのソースを表示」）
3. `G-BE9HZ0XGH4` が含まれているか確認

### 3. 開発者ツールで確認

1. 開発者ツール（F12）を開く
2. Networkタブを開く
3. ページをリロード
4. `gtag/js?id=G-BE9HZ0XGH4` のリクエストを確認

---

## トラブルシューティング

### 問題: Vercel CLIでログインできない

**解決策**:
- ブラウザで手動でログイン
- `vercel login` を再実行

### 問題: プロジェクトをリンクできない

**解決策**:
- Vercelダッシュボードでプロジェクト名を確認
- `vercel link` で正しいプロジェクト名を入力

### 問題: デプロイが失敗する

**解決策**:
- Vercelダッシュボードでエラーログを確認
- `vercel.json` の設定を確認
- Root Directoryが `landing` になっているか確認

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27

