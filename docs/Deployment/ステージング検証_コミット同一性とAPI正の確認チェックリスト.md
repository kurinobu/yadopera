# ステージング検証チェックリスト：実行コミット同一性と API の「正」の確認

**目的**: ステージングで「期待する表示・動作にならない」問題に対し、UI やキャッシュの議論に入る前に、外部観測で **(1) 実行コミット** と **(2) API が返す正の値** を確定し、原因を「アプリ不具合」か「デプロイ不整合」かに即座に切り分ける。
**作成日**: 2026-03-11  
**Status**: 再発防止用チェックリスト。指示があるまで実装・デプロイ操作は行わない。

---

## 1. 実行コミットの同一性（最優先）

1. 次を実行する。

```
GET https://yadopera-backend-staging.onrender.com/__debug_env
```

2. `RENDER_GIT_COMMIT` を確認する。

- **期待**: 検証対象ブランチ（通常 `develop`）の最新コミットと一致している。
- **不一致**: 未デプロイ、別ブランチ、別サービス参照（Blueprint 二重化など）を疑う。以降のアプリ調査は保留し、まずデプロイ経路を正す。

---

## 2. ゲスト言語（多言語）の正（公開 API 実測）

ゲスト画面の言語カードは **公開 API の `facility.available_languages` が唯一の正**。

### 2.1 施設 slug の取得

管理画面ログイン後、次を実行して `facility.slug` を取得する。

```
GET https://yadopera-backend-staging.onrender.com/api/v1/admin/facility/settings
```

### 2.2 公開 API の確認

取得した slug を使い、次を実行する。

```
GET https://yadopera-backend-staging.onrender.com/api/v1/facility/{slug}
```

確認項目:
- `facility.plan_type`
- `facility.available_languages`

期待値（多言語_5 反映後）:
- Premium: `["ja","en","zh-TW","zh-CN","fr","ko","es"]`

> 注意: ここが期待値でない限り、フロント側で Premium フォールバック等を入れて表示を合わせるのは **暫定解決**かつ **二重定義**であり不採用（大原則：根本解決、統一・同一化）。

---

## 3. ダッシュボード表示（プラン表示など）の正（レスポンス本文）

ダッシュボードの表示が期待どおりでない場合、まず **レスポンス本文**が期待値かどうかを切り分ける。

1. ブラウザの Network タブで `GET /api/v1/admin/dashboard` のレスポンス JSON を開く。
2. 例: `monthly_usage.plan_type` など「表示に使っているフィールド」を直接確認する。

---

## 4. 根本解決の基本方針（大原則）

- **根本解決 > 暫定解決**: まず「正しいコードがステージングで実行されている状態」を作る（マージ→デプロイ）。
- **統一・同一化 > 特殊独自**: 正は API で 1 箇所に集約し、フロントは API を表示するのみ。

