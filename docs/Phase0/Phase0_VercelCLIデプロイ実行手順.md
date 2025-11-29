# Vercel CLIデプロイ実行手順（詳細版）

**作成日**: 2025年11月27日  
**目的**: ターミナルでVercel CLIを使用してデプロイする手順

---

## 実行場所

**ターミナル（Terminal）アプリケーション**で実行します。

### Macの場合

1. **Spotlight検索**で「ターミナル」または「Terminal」と入力して起動
   - または `Cmd + Space` でSpotlight検索を開く
2. **Finder** → アプリケーション → ユーティリティ → ターミナル

### Windowsの場合

1. **コマンドプロンプト**または**PowerShell**を起動
2. Windowsキー + R → `cmd` と入力

---

## 実行手順

### ステップ1: プロジェクトディレクトリに移動

ターミナルで以下のコマンドを実行：

```bash
cd /Users/kurinobu/projects/yadopera/landing
```

**確認**: プロンプトに `landing` と表示されればOK

---

### ステップ2: Vercel CLIにログイン

```bash
vercel login
```

**実行結果**:
- ブラウザが自動的に開きます
- Vercelのログインページが表示されます
- ログイン後、ターミナルに「Success! Logged in as [あなたのメールアドレス]」と表示されます

**注意**: ブラウザが開かない場合は、表示されたURLをブラウザで開いてください

---

### ステップ3: 既存のプロジェクトにリンク

```bash
vercel link
```

**質問と回答**:

1. **Set up and deploy "~/projects/yadopera/landing"?**
   - → `Y` と入力してEnter

2. **Which scope should contain your project?**
   - → 個人アカウントを選択（矢印キーで選択してEnter）

3. **Link to existing project?**
   - → `Y` と入力してEnter

4. **What's the name of your existing project?**
   - → `yadopera-landing` と入力してEnter

5. **In which directory is your code located?**
   - → `.` と入力してEnter（現在のディレクトリ）

**確認**: 「Linked to [あなたのアカウント]/yadopera-landing」と表示されればOK

---

### ステップ4: 本番環境にデプロイ

```bash
vercel --prod
```

**実行結果**:
- デプロイが開始されます
- 数秒〜1分程度で完了します
- 「Production: https://yadopera.com [copied to clipboard]」と表示されれば完了

---

## 実行例（全体の流れ）

```bash
# ステップ1: ディレクトリに移動
cd /Users/kurinobu/projects/yadopera/landing

# ステップ2: ログイン
vercel login
# → ブラウザでログイン

# ステップ3: プロジェクトにリンク
vercel link
# → 質問に答える（上記参照）

# ステップ4: 本番環境にデプロイ
vercel --prod
# → デプロイ完了
```

---

## トラブルシューティング

### 問題1: `vercel: command not found`

**原因**: Vercel CLIがインストールされていない

**解決策**:
```bash
npm install -g vercel
```

### 問題2: ログインできない

**原因**: ブラウザが開かない、またはログインに失敗

**解決策**:
- ブラウザを手動で開く
- Vercelのアカウントでログインしているか確認
- `vercel login` を再実行

### 問題3: プロジェクトをリンクできない

**原因**: プロジェクト名が間違っている、または存在しない

**解決策**:
- Vercelダッシュボードでプロジェクト名を確認
- 正しいプロジェクト名を入力（`yadopera-landing`）

### 問題4: デプロイが失敗する

**原因**: 設定ファイルの問題、または権限の問題

**解決策**:
- エラーメッセージを確認
- `vercel.json` の設定を確認
- Vercelダッシュボードでエラーログを確認

---

## 確認方法

デプロイ完了後、以下を確認：

1. **Vercelダッシュボード**
   - 最新のデプロイが完了しているか
   - コミット: `4eddb00` または `46a7aba` が含まれているか

2. **ブラウザ**
   - `https://yadopera.com` にアクセス
   - ページのソースを表示（右クリック → 「ページのソースを表示」）
   - `G-BE9HZ0XGH4` が含まれているか確認

3. **開発者ツール**
   - 開発者ツール（F12）→ Networkタブ
   - `gtag/js?id=G-BE9HZ0XGH4` のリクエストを確認

---

## 補足: ターミナルの使い方

### コマンドの実行方法

1. ターミナルを開く
2. コマンドを入力
3. Enterキーを押す

### コピー&ペースト

- **Mac**: `Cmd + C`（コピー）、`Cmd + V`（ペースト）
- **Windows**: `Ctrl + C`（コピー）、`Ctrl + V`（ペースト）

### 現在のディレクトリを確認

```bash
pwd
```

### ファイル一覧を表示

```bash
ls
```

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27

