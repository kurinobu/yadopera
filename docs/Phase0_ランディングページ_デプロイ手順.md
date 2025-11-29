# ランディングページ デプロイ手順（Vercel）

**作成日**: 2025年11月25日  
**目的**: ランディングページをVercelにデプロイし、Google Analyticsを設定する手順

---

## ⚠️ 重要なポイント

**ランディングページはRender.comとは完全に独立しています。**

- **ランディングページ**: Vercelにデプロイ（静的HTML）
- **本番アプリ**: Render.comにデプロイ（Phase 1 Week 4以降）
- **両者は別物で、ランディングページはPhase 0完了後すぐにデプロイ可能**

---

## デプロイ手順

### ステップ1: Vercelアカウント準備

1. [Vercel](https://vercel.com/)にアクセス
2. GitHubアカウントでログイン
3. アカウント作成完了

### ステップ2: プロジェクト作成

1. Vercelダッシュボードで「New Project」をクリック
2. GitHubリポジトリ（`kurinobu/yadopera`）を選択
3. **Root Directory**: `landing` を指定
4. **Framework Preset**: Other（またはStatic Site）
5. **Build Command**: なし（静的HTMLのため）
6. **Output Directory**: `.`（ルートディレクトリ）
7. 「Deploy」をクリック

### ステップ3: カスタムドメイン設定

1. デプロイ完了後、プロジェクト設定を開く
2. 「Domains」タブを選択
3. `tabipera.com` を追加
4. DNS設定を指示に従って実施
5. SSL証明書は自動で設定される

### ステップ4: Google Analytics設定

1. **Google Analytics 4プロパティ作成**
   - [Google Analytics](https://analytics.google.com/)にアクセス
   - 「管理」→「プロパティを作成」
   - プロパティ名: 「やどぺら LP」
   - **ウェブサイトURL**: `https://tabipera.com`（Vercelデプロイ後のURL）
   - レポートのタイムゾーン: 「日本標準時」
   - 通貨: 「日本円 (¥)」

2. **測定ID取得**
   - 「管理」→「データストリーム」→「ウェブ」を選択
   - 測定ID（`G-XXXXXXXXXX`形式）をコピー

3. **HTMLに測定ID設定**
   - `landing/index.html`を編集
   - 23行目と28行目の`G-XXXXXXXXXX`を実際の測定IDに置き換え
   - コミット・プッシュ
   - Vercelが自動で再デプロイ

### ステップ5: 動作確認

1. `https://tabipera.com` にアクセス
2. ページが正常に表示されることを確認
3. 開発者ツール（F12）でGoogle Analyticsのリクエストが送信されているか確認
4. Google Analyticsのリアルタイムレポートでアクセスが記録されているか確認

---

## タイムライン

| ステップ | 時期 | 所要時間 |
|---------|------|---------|
| Vercelデプロイ | Phase 0完了後、すぐに実施可能 | 30分 |
| カスタムドメイン設定 | デプロイ後 | 10分（DNS設定含む） |
| Google Analytics設定 | デプロイ後 | 30分 |
| **合計** | **Phase 0完了後、すぐに実施可能** | **約1時間** |

---

## Render.comとの関係

### 混同しやすいポイント

❌ **誤解**: Render.comのサービス立ち上げを待たないとランディングページがデプロイできない

✅ **正解**: ランディングページはVercelにデプロイするため、Render.comとは無関係

### 実際の関係

```
【ランディングページ（Vercel）】
Phase 0完了 → すぐにデプロイ可能 → Google Analytics設定可能

【本番アプリ（Render.com）】
Phase 1 Week 4 → ステージング環境構築
Phase 4 → 本番環境構築

→ 両者は完全に独立している
```

---

## トラブルシューティング

### 問題: Vercelデプロイが失敗する

**解決策**:
- `landing/vercel.json`が正しく設定されているか確認
- Root Directoryが`landing`に設定されているか確認

### 問題: カスタムドメインが設定できない

**解決策**:
- DNS設定が正しく行われているか確認
- ドメインの所有権を確認

### 問題: Google Analyticsが動作しない

**解決策**:
- 測定IDが正しく設定されているか確認
- ブラウザの拡張機能（広告ブロッカー等）を確認
- Google Analyticsのリアルタイムレポートで確認

---

## 次のアクション

### すぐに実施可能（Phase 0完了後）

1. ✅ Vercelにランディングページをデプロイ
2. ✅ カスタムドメイン設定（tabipera.com）
3. ✅ Google Analytics 4プロパティ作成
4. ✅ 測定IDをHTMLに設定
5. ✅ ランディングページ公開完了

### 後で実施（Phase 1以降）

- Render.comステージング環境構築（Phase 1 Week 4）
- Render.com本番環境構築（Phase 4）

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-25  
**Status**: 手順完成

