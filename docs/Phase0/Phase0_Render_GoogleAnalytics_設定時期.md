# Render.comサービス立ち上げ時期とGoogle Analytics設定の関係

**作成日**: 2025年11月25日  
**目的**: Render.comサービス立ち上げ時期とGoogle Analytics設定のタイミングを明確化

---

## 調査結果

### Render.comサービス立ち上げ時期

#### 1. ステージング環境
- **時期**: **Phase 1 Week 4（統合・テスト）**
- **内容**:
  - `develop`ブランチ作成
  - Render.comステージングサービス作成
  - Railway Hobby PostgreSQL設定
  - Railway Hobby Redis設定
  - ステージング環境変数設定
  - ステージング環境デプロイ確認
- **URL**: `https://staging.yadopera.com`（予定）

#### 2. 本番環境
- **時期**: **Phase 4（本格展開準備、1ヶ月）**
- **内容**:
  - Render.com本番サービス作成
  - Render.com PostgreSQL（Managed）作成
  - Redis Cloud設定
  - 本番環境変数設定
  - カスタムドメイン設定（yadopera.com）
  - SSL証明書設定
  - 本番環境デプロイ確認
- **URL**: `https://yadopera.com`（予定）

### ランディングページのデプロイ

**重要**: ランディングページは**Render.comではなくVercel**にデプロイします。

- **デプロイ先**: Vercel
- **カスタムドメイン**: `https://yadopera.com`（または`https://www.yadopera.com`）
- **デプロイ時期**: Phase 0完了後またはPhase 1開始前（PoC募集開始前）

---

## Google Analytics設定のタイミング

### 問題点

**Google Analytics 4の設定には実際のURLが必要**ですが、現在の状況：

1. **ランディングページ**: 
   - 実装済み（Phase 0 ステップ10完了）
   - Google Analytics 4コード実装済み
   - **測定ID未設定**（G-XXXXXXXXXXのまま）
   - **デプロイ未完了**（Vercelにデプロイしていない）

2. **Google Analytics設定**:
   - プロパティ作成時に「ウェブサイトURL」の入力が必要
   - 現在はデプロイされていないため、実際のURLが確定していない

### 解決策

#### オプション1: 一時的にlocalhostを入力（推奨）

1. **Google Analytics 4プロパティ作成時**:
   - ウェブサイトURL: `http://localhost:8001`（一時的）
   - 後で更新可能（設定→データストリーム→編集）

2. **Vercelデプロイ後**:
   - データストリームのURLを`https://yadopera.com`に更新
   - 測定IDをHTMLに設定

#### オプション2: デプロイ後に設定（推奨）

1. **Vercelにランディングページをデプロイ**（Phase 0完了後）
2. **カスタムドメイン設定**（yadopera.com）
3. **Google Analytics 4プロパティ作成**（実際のURLで作成）
4. **測定IDをHTMLに設定**

### 推奨フロー

```
Phase 0完了
  ↓
Vercelにランディングページデプロイ
  ↓
カスタムドメイン設定（yadopera.com）
  ↓
Google Analytics 4プロパティ作成（URL: https://yadopera.com）
  ↓
測定ID取得
  ↓
HTMLに測定ID設定
  ↓
Google Analytics設定完了
```

---

## Render.comとGoogle Analyticsの関係

### 重要なポイント

**Render.comのサービス立ち上げとランディングページのGoogle Analytics設定は直接関係ありません。**

- **Render.com**: 本番アプリ（FastAPI + Vue.js）用
- **ランディングページ**: Vercelにデプロイ（静的HTML）
- **Google Analytics**: ランディングページ用（Vercelデプロイ後に設定）

### タイムライン

| フェーズ | 時期 | Render.com | ランディングページ | Google Analytics |
|---------|------|------------|-------------------|-----------------|
| Phase 0 | 1週間 | - | ✅ 実装完了 | ⏳ 測定ID未設定 |
| Phase 0完了後 | - | - | ⏳ Vercelデプロイ | ⏳ プロパティ作成・設定 |
| Phase 1 Week 4 | 4週目 | ⏳ ステージング環境構築 | - | - |
| Phase 4 | 1ヶ月 | ⏳ 本番環境構築 | - | - |

---

## 次のアクション

### 優先度: 高

1. **Vercelにランディングページをデプロイ**
   - Phase 0完了後、すぐに実施可能
   - カスタムドメイン設定（yadopera.com）

2. **Google Analytics 4プロパティ作成**
   - デプロイ後の実際のURLで作成
   - 測定ID取得

3. **HTMLに測定ID設定**
   - `landing/index.html`の`G-XXXXXXXXXX`を実際の測定IDに置き換え

### 優先度: 中

4. **Render.comステージング環境構築**
   - Phase 1 Week 4で実施
   - 本番アプリのテスト用

5. **Render.com本番環境構築**
   - Phase 4で実施
   - PoC成功後の本格展開準備

---

## 結論

### ⚠️ 重要な誤解の解消

**Render.comのサービス立ち上げを待つ必要はありません！**

1. **ランディングページのデプロイ**:
   - **Vercelにデプロイ**（Render.comとは完全に独立）
   - **Phase 0完了後、すぐにデプロイ可能**
   - Render.comのサービス立ち上げとは無関係

2. **Google Analytics設定**:
   - **Vercelデプロイ後、すぐに設定可能**
   - Render.comのサービス立ち上げを待つ必要はない
   - デプロイ前でも一時的にlocalhostでプロパティ作成可能（後でURL更新）

3. **Render.comサービス立ち上げ**（本番アプリ用）:
   - ステージング: Phase 1 Week 4
   - 本番: Phase 4
   - **ランディングページとは別物**

### 推奨順序（ランディングページ）

```
Phase 0完了（現在）
  ↓
【すぐに実施可能】Vercelにランディングページをデプロイ
  ↓
【すぐに実施可能】カスタムドメイン設定（yadopera.com）
  ↓
【すぐに実施可能】Google Analytics 4プロパティ作成
  ↓
【すぐに実施可能】測定IDをHTMLに設定
  ↓
ランディングページ完成・公開完了
```

**Render.comのサービス立ち上げは不要です！**

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-25  
**Status**: 調査完了

