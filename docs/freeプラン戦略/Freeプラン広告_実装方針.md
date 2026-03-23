# Freeプラン ゲスト画面固定フッター広告 実装方針

**作成日**: 2026-03-04  
**参照**: 要約定義書 v0.3、Phase3 現況、アーキテクチャ設計書

**Freeプラン広告に関する文書（本フォルダ内）**
- `free_plan_ad_strategy.md` — Freeプラン広告実装戦略計画書（目的・前提・広告方式・表示位置・DB/API仕様・KPI等）
- `Freeプラン広告_実装方針.md` — 本ドキュメント（実装計画・PR表示・アフィリエイト仕様）

---

## 1. 目的・全体像・経緯の把握（参照文書より）

### 1.1 目的（要約定義書・Phase3）
- **やどぺら**: 小規模宿泊施設向け外国人ゲスト対応自動化SaaS。QRコードでAIが24時間多言語自動応答。
- **大原則**: 根本解決 > 暫定解決、シンプル構造 > 複雑構造、統一・同一化 > 特殊独自、拙速 < 安全確実、Docker環境必須。

### 1.2 Freeプラン広告の目的（free_plan_ad_strategy.md）
- **目的A**: Freeユーザーからの直接収益化（サーバー費用回収・運用費補填・黒字化の加速）
- **目的B**: 有料プランへのアップグレード動機形成（広告非表示を有料特典とするUX差別化）

### 1.3 表示ルール（戦略書）
- **Free**: 広告表示あり
- **Mini以上**: 広告非表示（アップグレード誘導）

### 1.4 表示位置（戦略書）
- **最適位置**: ゲストチャット画面下部（固定フッター）
- **禁止位置**: チャット回答内、UI中央、回答直後（UX保護）

---

## 2. 現況（コードベース調査結果）

### 2.1 ゲスト画面・固定フッター
- **GuestLayout.vue**  
  - ゲスト全画面（言語選択・ウェルカム・チャット）を包む共通レイアウト。  
  - **オプション用固定フッター**: `GuestOptionFooter` を表示。  
  - 表示条件: `showOptionFooter = !!facility?.coupon?.enabled`（クーポン有効時のみ）。
- **GuestOptionFooter.vue**  
  - 固定フッター内でクーポンCTAボタンのみ実装。横スクロール対応で「後続オプション（延長・延泊等）」の追加を想定したコメントあり。
- **Chat.vue**  
  - チャット画面。メッセージ入力欄が画面下部に固定されているが、これは「入力欄」であり、広告用の固定フッターとは別。

### 2.2 施設情報・プラン
- **ゲスト向けAPI**: `GET /api/v1/facility/{slug}` で施設情報を取得。  
  - レスポンスに **plan_type** を含む（Free, Mini, Small, Standard, Premium）。
- **フロント**: `stores/facility.ts` の `currentFacility`、型 `Facility`（`types/facility.ts`）に **plan_type?: string** あり。  
  - ゲストは施設取得時に既に `plan_type` を保持可能。

### 2.3 広告まわり
- **ads テーブル**: 未実装。
- **API `/api/v1/ads`**: 未実装。
- **フロントの広告表示**: 未実装。

### 2.4 添付文書との整合性
- **free_plan_ad_strategy.md**  
  - 実装仕様: DB `ads`、API `/api/v1/ads`（Freeプラン時のみ返却）、フロントは「GuestChat.vue」で Free 時のみ表示、と記載。  
  - 実際の構成では「ゲストチャット画面」は `GuestLayout` 配下の一画面であり、固定フッターは **GuestLayout** の `GuestOptionFooter` で共通。  
  - よって「ゲスト画面の固定フッターに広告」＝**GuestLayout の固定フッター（GuestOptionFooter を拡張するか、同エリアに広告ブロックを追加）で Free のときのみ表示**とするのが、既存パターンと一致し整合的。

※ **yadopera_ad_impl_spec_v2.docx** はリポジトリ内に存在せず未参照。必要であれば内容を共有いただければ方針に反映する。

---

## 3. 期待する機能と表示

### 3.1 期待する機能
1. **Freeプラン限定表示**  
   - 施設の `plan_type === 'Free'` のときのみ、ゲスト画面の固定フッターに広告を表示する。  
   - Mini / Small / Standard / Premium では一切表示しない。
2. **広告データの取得**  
   - ゲストが施設ページにアクセスしたとき、当該施設が Free の場合に限り、広告一覧を取得する（例: `GET /api/v1/ads`）。  
   - バックエンドは Free の施設からのリクエスト時のみ広告を返す（他プランは空 or 404 でよい）。
3. **表示位置**  
   - 既存の「オプション用固定フッター」と同じ領域（画面最下部固定）。  
   - クーポン有効時は「クーポンボタン ＋ 広告」を横並び（または広告をその下/右に配置）し、クーポン無効時は広告のみ表示。  
   - チャット回答内・UI中央・回答直後には出さない（戦略書どおり）。
4. **クリック動作**  
   - 各広告はアフィリエイトURL（`affiliate_url`）で新しいタブを開く。  
   - リンクには **`target="_blank"`** および **`rel="nofollow sponsored noopener"`** を必ず付与する（アフィリエイト・外部リンクのガイドライン準拠）。計測が必要ならクリックログは将来拡張で検討。

### 3.2 期待する表示
- **見た目**  
  - 「おすすめ情報」などの見出し＋複数リンク（例: 「近くの宿を探す（楽天トラベル）」「周辺の観光体験を見る（アソビュー）」）。  
  - 既存のダークモード・セーフエリア（safe-area）に合わせる。
- **PR表示（必須・法律対応）**  
  - 広告であることを明示するため、**法律に則り必ず「PR」を表示する**。  
  - 景品表示法・広告ガイドラインに基づく表記。広告ブロックの見出し付近または広告一覧の直上/直下に「PR」を常時表示する。
- **UX**  
  - 固定フッターは既存と同様、横スクロール可能で、クーポンと広告が並んでもはみ出さない。  
  - 文言は戦略書の「日本語限定」を踏まえ、初期は日本語表記でよい（多言語は将来拡張可）。

---

## 4. 実装方針（指示があるまで実装しない）

### 4.1 バックエンド
1. **DB**  
   - **ads** テーブルを新規作成（Alembic マイグレーション）。  
   - 項目: id, title, description, url, affiliate_url, priority, active, (created_at, updated_at 等)。  
   - 戦略書の「id title description url affiliate_url priority active」に合わせる。
2. **API**  
   - **GET /api/v1/ads**（または `/api/v1/guest/ads`）を追加。  
   - クエリまたはヘッダーで「施設ID or slug」を受け取り、その施設の `plan_type` が Free の場合のみ広告一覧を返す。  
   - 他プランなら空配列 or 204 で返し、ゲスト側で表示しない。
3. **認証**  
   - ゲスト向けのため認証不要。施設識別子でプラン判定する。

### 4.2 フロントエンド
1. **表示条件**  
   - `GuestLayout` で `facility?.plan_type === 'Free'` のとき、固定フッターを表示する条件に「広告表示」を追加。  
   - 現状は `showOptionFooter = !!facility?.coupon?.enabled` のみのため、**広告は Free のときは常に表示**するなら `showOptionFooter = !!facility?.coupon?.enabled || facility?.plan_type === 'Free'` のように変更し、`GuestOptionFooter` 内で「Free のとき広告ブロックを表示」とする。
2. **広告ブロック**  
   - `GuestOptionFooter.vue` 内に、Free のときだけ表示する「おすすめ情報」セクションを追加。  
   - または `GuestAdBlock.vue` を新規作成し、`GuestOptionFooter` から `v-if="facility?.plan_type === 'Free'"` で呼び出す。
3. **データ取得**  
   - 施設取得後、`plan_type === 'Free'` のときだけ `GET /api/v1/ads`（施設ID/slug付き）を呼び、結果を固定フッターに表示。  
   - キャッシュは既存の施設ストアやコンポーネント内 ref で保持すればよい。
4. **表示内容**  
   - **「PR」を必ず表示**（法律に則った広告明示）。見出し「おすすめ情報」の近くまたは広告一覧の直上に「PR」を表示。  
   - 見出し「おすすめ情報」＋各広告をリンク（`affiliate_url`）で表示。リンクは `target="_blank"` と `rel="nofollow sponsored noopener"` を付与。  
   - デザインは既存のクーポンボタンや Tailwind のスタイルに合わせ、ダークモード・セーフエリア対応。

### 4.3 アフィリエイトリンク仕様（使用するコード）

**楽天トラベル（Phase 1 で使用するアフィリエイト）**

以下をそのまま使用する。

- **affiliate_url**（DBの `affiliate_url` に登録する値）:
  ```
  https://hb.afl.rakuten.co.jp/hgc/15132e76.272ee056.15132e77.f62b93e1/?pc=https%3A%2F%2Ftravel.rakuten.co.jp%2F&link_type=text&ut=eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9
  ```
- **表示用テキスト**: 「PR：次の旅行先の宿を探す（楽天トラベル）」
- **リンク属性（フロントで必ず付与）**:
  - `target="_blank"`
  - `rel="nofollow sponsored noopener"`
- **HTML例（実装時の参照）**:
  ```html
  <a href="[上記affiliate_url]" target="_blank" rel="nofollow sponsored noopener">PR：次の旅行先の宿を探す（楽天トラベル）</a>
  ```

Phase 2 以降でじゃらん・アソビュー等を追加する場合も、同様に `affiliate_url` と表示文言を `ads` に登録し、リンクには上記 `target` / `rel` を付与する。

### 4.4 データ・運用
- **Phase 1（戦略書）**: 上記楽天トラベルアフィリエイトを `ads` に1件登録し、Free 施設で表示。  
- 管理画面での広告 CRUD は今回のスコープ外でも可（シード or 手動DBで投入）。必要なら後から管理APIを追加。

### 4.5 大原則との整合
- **シンプル構造**: 既存の GuestOptionFooter を拡張し、新規画面は増やさない。  
- **統一**: ゲスト向け公開API・既存の facility/plan_type の扱いと統一。  
- **安全確実**: Docker で動作確認し、Free 以外で広告が表示されないことをテストで担保する。

---

## 5. まとめ

| 項目 | 内容 |
|------|------|
| 対象 | Freeプランの施設のゲスト画面のみ |
| 表示場所 | ゲスト画面の固定フッター（GuestLayout 配下の GuestOptionFooter 領域） |
| PR表示 | **必須**。法律に則り広告であることを明示する「PR」を必ず表示する |
| リンク属性 | `target="_blank"` および `rel="nofollow sponsored noopener"` を付与 |
| バックエンド | ads テーブル新設、GET /api/v1/ads（Free 時のみ返却） |
| フロント | GuestOptionFooter の表示条件に Free を追加し、Free のとき広告ブロックを表示 |
| 期待表示 | 「PR」＋「おすすめ情報」＋アフィリエイトリンク（Phase 1: 楽天トラベル） |
| 参照文書 | `docs/freeプラン戦略/` 内の free_plan_ad_strategy.md および本ドキュメント |

**楽天トラベルアフィリエイト**: 本文書 4.3 節の URL とリンク属性を使用する。

---

## 6. 実施記録（4.1 バックエンド）

- **バックアップ**: `backups/20260304_free_plan_ads_41_backend/`（実装前の models, schemas, api/v1, alembic/versions を保存）
- **実施日**: 2026-03-04
- **実装内容**:
  - **ads テーブル**: マイグレーション 019 で作成（id, title, description, url, affiliate_url, priority, active, created_at, updated_at）
  - **シード**: マイグレーション 020 で楽天トラベル1件を登録（表示テキスト: 「PR：次の旅行先の宿を探す（楽天トラベル）」）
  - **モデル**: `app/models/ad.py`（Ad）
  - **スキーマ**: `app/schemas/ad.py`（AdItem, AdListResponse）
  - **API**: `GET /api/v1/ads?facility_slug={slug}` または `?facility_id={id}`。施設が Free のときのみ広告一覧を返却。他プラン・未指定時は空配列。
- **Docker**: `alembic upgrade head` で 019・020 を適用済み。

---

## 7. 実施記録（4.2 フロントエンド）

- **バックアップ**: `backups/20260304_free_plan_ads_42_frontend/`（GuestLayout.vue, GuestOptionFooter.vue を保存）
- **実施日**: 2026-03-04
- **実装内容**:
  - **GuestLayout.vue**: `showOptionFooter` を「クーポン有効 **または** plan_type === Free」に変更。Free のときも固定フッターを表示。
  - **api/ads.ts**: 新規。`adsApi.getAds({ facility_slug, facility_id })` で GET /api/v1/ads を呼び出し。
  - **GuestOptionFooter.vue**: Free プラン時に「PR」「おすすめ情報」を表示し、取得した広告を `target="_blank"` と `rel="nofollow sponsored noopener"` 付きのリンクで表示。表示テキストは API の title（楽天トラベルは「PR：次の旅行先の宿を探す（楽天トラベル）」）。

**動作・表示確認（2026-03-04 ローカル Docker）**
- **Docker**: `docker compose up -d` で postgres / redis / backend / frontend 起動済み。
- **フロントビルド**: `npm run build` で vue-tsc および Vite バンドルまで成功（PWA SW 書き出しは既存事象で別要因）。
- **API**:
  - `GET /api/v1/ads?facility_slug=test-facility-2025`（Free）→ 楽天トラベル1件返却。
  - `GET /api/v1/ads?facility_slug=testhotel-7ee91d05`（Premium）→ `{"ads":[]}`。
- **ブラウザ**: `http://localhost:5173/f/test-facility-2025` でゲスト言語選択画面を表示。固定フッターに「PR」「おすすめ情報」および「PR：次の旅行先の宿を探す（楽天トラベル）」リンクが表示されることを確認済み。
