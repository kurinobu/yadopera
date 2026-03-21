# LP・ティザー GitHub Pages デプロイ不手際と是正の記録

**作成日**: 2026年3月21日  
**目的**: `yadopera.com` が更新されない事象の原因分析、是正内容、再発防止を文書化する。  
**ステータス**: 是正完了（本番URLで反映を確認済み）

---

## 1. 事象

- **2026-03-21 時点**: `landing/` の文案修正（ティザー：宿泊施設実証実験表記・運営者情報・やどびと等、本番LP：`develop` 上の `index.html`）を実施し、`develop` へコミット・プッシュした。
- **利用者の認識**: 「デプロイ完了」後も **`https://yadopera.com` の表示が古いまま**（例：「PoC（実証実験）」表記のまま）。GitHub の **`main` ブランチ上の `landing/index.html`** も更新されていないように見えた。

---

## 2. 根本原因（確定）

| 要因 | 説明 |
|------|------|
| **デプロイ経路の取り違え** | **`yadopera.com` は GitHub Pages**（`.github/workflows/pages.yml`）。**トリガーは `main` への push かつ `landing/**` の変更のみ**。`develop` への push では **Pages は一切走らない**。 |
| **ブランチ戦略との関係** | 要約定義書・総括どおり **`main`＝本番系、`develop`＝ステージング** だが、**静的 LP の「本番URL」は `main` の `landing/` だけ**がソースである点を、作業完了報告で十分に前面に出せていなかった。 |
| **Render デプロイとの混同** | `develop` push で **Render（`yadopera-frontend-staging` 等）が更新**されても、それは **Vue フロント SPA** のパイプライン。**`landing/` の静的サイトとは別**である。 |

**結論**: 不具合ではなく、**`main` に反映していないため本番ドメインが変わらなかった**。

---

## 3. 是正内容（実施済み）

| 項目 | 内容 |
|------|------|
| **コミット（develop）** | `015bf43` — `landing/index.html`（本番LP）、`landing/teaser-index.html`（ティザー差し替え元）、`landing/legal/operation.html`・`tokusho.html` 等。 |
| **コミット（main）** | `e6831dd` — `origin/develop` の **`landing/teaser-index.html` と同一内容**で **`main` の `landing/index.html` を上書き**し push。 |
| **結果** | GitHub Actions「Deploy to GitHub Pages」が `main` push で実行され、**利用者が本番URLでの反映を確認**。 |

### 3.1 運用上の決め（現状）

- **`develop` の `landing/index.html`**: 本番向け LP（LP v1.0 系）の作業用。ステージングとは別（Render は `frontend/` をビルド）。
- **`main` の `landing/index.html`**: **`https://yadopera.com/` に出す中身**（当面はティザー）。更新時は **必ず `main` に取り込む**。
- **`develop` の `landing/teaser-index.html`**: **`main` の `index.html` と揃えるための差し替え元**として追加。ティザー修正のフローは「`teaser-index.html` を編集 → `main` の `index.html` に同期 → `main` push」が明確。

---

## 4. 教訓・チェックリスト（再発防止）

**LP／ティザーを `yadopera.com` で確認したいとき**

1. [ ] 変更が **`origin/main` の `landing/`** に入っているか（GitHub 上でブランチを `main` にして確認）。
2. [ ] **Actions** で「Deploy to GitHub Pages」が成功しているか。
3. [ ] ブラウザで **スーパーリロード**（キャッシュの影響を疑う場合）。

**「デプロイした」の意味を言語化する**

- **Render ステージング**: `develop` → アプリ本体。
- **GitHub Pages**: `main` + `landing/**` → **`yadopera.com`**。

---

## 5. 関連ファイル・参照

| 種別 | パス |
|------|------|
| Pages ワークフロー | `.github/workflows/pages.yml` |
| ティザー差し替え元（develop） | `landing/teaser-index.html` |
| 本番URLの実体（main） | `landing/index.html`（ティザー運用時） |
| ブランチ戦略・大原則 | `docs/20260307_プロジェクト現況と今後の計画_総括.md` §0.3 |
| ティザー切替の歴史 | `docs/20260121_ティザーサイト切り替え完了_引き継ぎ書.md`（§追記） |
| LP 本番公開の順序 | `docs/サービス開始までの手順整理_実装計画.md` §6.1・§6.2 |
| ランディング README | `landing/README.md` |

---

**Document Version**: 1.0  
**Last Updated**: 2026年3月21日
