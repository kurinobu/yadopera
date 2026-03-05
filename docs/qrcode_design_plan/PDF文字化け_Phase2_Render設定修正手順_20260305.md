# PDF文字化け Phase 2 — Render 設定修正手順（2026-03-05）

**前提**: Phase 1 の観測で **ケース A** と判定（想定 Docker イメージが実行されていない）。  
**目的**: Render のバックエンドサービスを **Docker ビルド・Docker 実行** に切り替え、再観測で同一性を確認する。

---

## 0. 訂正（憶測による誤記載の削除）

**「Settings → Build & Deploy の Environment / Language を Docker に変更する」という説明は誤りでした。**

- 共有いただいた **Render ダッシュボードのスクショ** を確認した結果、**Build & Deploy 画面には「Language」「Environment」を Docker に切り替える項目は存在しません。**
- Render 公式: 既存サービスの **runtime は Dashboard では変更できない**。**Blueprint（render.yaml）の更新と同期** または **API** でのみ変更可能（[Changelog: Change runtime via API or Blueprint](https://render.com/changelog/change-an-existing-services-runtime-via-api-or-blueprint)）。
- 上記の誤った手順で混乱を招いたことをお詫びします。以下は **事実と公式仕様に基づく** 手順に差し替えています。

---

## 1. スクショから分かったこと（設定確認結果）

共有いただいた Render 設定画面から、以下が確認できました。

| 項目 | 現在の設定 | 問題 |
|------|------------|------|
| **Repository** | https://github.com/kurinobu/yadopera | 問題なし |
| **Branch** | develop | 問題なし |
| **Root Directory** | backend | 問題なし（Docker 利用時もこのままでよい） |
| **Build Command** | `pip install -r requirements.txt && alembic up...` | **ここが原因。** この指定により Render は **ネイティブ Python ビルド** を行い、**Dockerfile を使っていない**。 |
| **Start Command** | `uvicorn app.main:app --host 0.0.0.0 --port $P...` | ネイティブ Python 用。Docker に切り替えると Dockerfile の CMD が使われる。 |
| **Pre-Deploy Command** | （空） | 空。Docker 利用時はマイグレーションをここで回す想定。 |

**結論**: **Build Command に `pip install ...` が指定されているため、Render は Docker ではなく「ソースを展開して pip install するネイティブ Python 環境」でビルド・実行している。** その結果、cwd が `/opt/render/project/src/backend` となり、Dockerfile の `/app`・BUILD_MARKER・フォントが一切反映されない。  
**Runtime の切り替えは Dashboard の UI では行えず、Blueprint（render.yaml）の修正と Blueprint 同期で行う。**

---

## 2. Phase 2 で行うこと（実施内容）

### 2.1 リポジトリ側: render.yaml の修正（事実・仕様に基づく）

1. **`runtime: docker` を明示する**
   - Blueprint 仕様では `runtime` は必須。未記載だと既存サービスは「現在の runtime を維持」する。**Docker で動かすには `runtime: docker` を明示する必要がある。**

2. **Docker 用のフィールドだけにする**
   - **buildCommand**: 仕様上「**non-Docker** のときに必須」。Docker の場合は指定しない（指定するとネイティブ扱いになる可能性があるため削除）。
   - **startCommand**: 同様に non-Docker 用。Docker の場合は **dockerCommand** で上書きするか、省略して Dockerfile の `CMD` に任せる。
   - **preDeployCommand**: マイグレーション用に `alembic upgrade head` を指定する（Docker イメージ内で実行される想定）。
   - **dockerfilePath / dockerContext**: 既存の `./backend/Dockerfile` と `./backend` を維持。

3. **rootDir**
   - モノレポのため `rootDir: backend` を指定し、ビルドコンテキストと整合させる。

上記を反映した **render.yaml の修正例** は本文書の **§3** に記載する。修正後は **コミット・プッシュ** する。

### 2.2 Render 側: Blueprint の同期（Dashboard に「Language」は無い）

- **Runtime の変更は Dashboard の Build & Deploy では行えない。** 必ず **Blueprint（render.yaml）を更新し、Blueprint を同期** する。
- 手順:
  1. 上記のとおり **render.yaml を修正してコミット・プッシュ** する。
  2. Render ダッシュボードで、**このリポジトリに紐づく Blueprint** のページを開く（サービス個別の Settings ではなく、「Blueprint」や「Infrastructure as Code」で作成した Blueprint 一覧から該当するもの）。
  3. その Blueprint の **「Manual Sync」**（または自動同期が有効なら push で自動同期）を実行する。
  4. 同期後、該当サービスが **Docker ビルド** で再デプロイされる。必要なら **Clear build cache & deploy** を 1 回実行する。

**Blueprint をまだ使っていない場合**（サービスを手動で作成しただけの場合）:

- まず **New > Blueprint** でリポジトリを Connect し、既存の `render.yaml` で Blueprint を作成する。サービス名が `yadopera-backend-staging` のままなら、Render は既存サービスに Blueprint の設定を適用する（[Adding an existing resource](https://render.com/docs/infrastructure-as-code)）。そのうえで上記の同期を行う。

### 2.3 再観測（同一性の確認）

デプロイ完了後、次を 1 回だけ実行する。

- **GET** `https://yadopera-backend-staging.onrender.com/__debug_env`

期待する結果（Docker イメージで動いている場合）:

- **cwd**: `/app`
- **app_list**: ディレクトリ一覧（`app`, `alembic`, `fonts` 等）
- **app_fonts_list**: ディレクトリ一覧または `NOT_FOUND`（現行 Dockerfile は fonts を COPY していないため、42f3e1e 系のままなら NOT_FOUND でも可）
- **build_marker**: `BUILD_MARKER_20260305_001`

これらが満たされれば、**実行環境が想定した Docker イメージと同一**と判断できる。その後に Dockerfile で IPA フォントを追加すれば、PDF 文字化け解消が期待できる。

---

## 3. render.yaml の修正例（§2.1 の具体形）

バックエンドサービスを **runtime: docker** にし、Docker 用フィールドだけにした例を以下に示す。`buildCommand` を削除し、`preDeployCommand` でマイグレーション、`dockerfilePath` / `dockerContext` を維持する。

```yaml
services:
  - type: web
    name: yadopera-backend-staging
    runtime: docker
    rootDir: backend
    dockerfilePath: ./Dockerfile
    dockerContext: .
    region: tokyo
    plan: pro
    preDeployCommand: alembic upgrade head
    envVars:
      # ... 既存の envVars をそのまま ...
    healthCheckPath: /api/v1/health
```

- **rootDir: backend** を指定している場合、`dockerfilePath` は **リポジトリルート基準** ではなく **rootDir 基準** になる仕様のため、`./Dockerfile`（backend 直下の Dockerfile）とする。`dockerContext: .` は rootDir からの相対で、backend がコンテキストになる。
- リポジトリルート基準のままにする場合は `dockerfilePath: ./backend/Dockerfile`, `dockerContext: ./backend` でよい（rootDir 未指定の場合）。

**本リポジトリでの反映**: `render.yaml` に **runtime: docker** を追加し、**buildCommand** と **startCommand** を削除、**preDeployCommand: alembic upgrade head** を追加済み。rootDir は未指定のまま、`dockerfilePath: ./backend/Dockerfile` と `dockerContext: ./backend` を維持している。

---

## 4. 補足（render.yaml と Dashboard の関係）

- **Runtime は Dashboard では変更できない。** Build & Deploy に「Language」「Environment」を選ぶ項目は **存在しない**（ユーザー確認・スクショのとおり）。
- 設定の単一の真実は **Blueprint（render.yaml）**。render.yaml に `runtime: docker` を明示し、**Blueprint を同期**することで既存サービスの runtime が Docker に変更される（Render Changelog 2024-05-24）。
- Dashboard で手動設定した **Build Command（pip install...）** は、Blueprint 同期時に **render.yaml の内容で上書き** される。そのため、**YAML で buildCommand を削除し、runtime: docker のみを指定する** ことが必要。

---

## 5. バックアップ

- **backups/20260305_phase2/** に以下を保存済み。
  - `render.yaml`
  - `PDF文字化け_Phase1_観測結果と解釈_20260305.md`

---

**記録日**: 2026-03-05  
**次のアクション**: リポジトリで render.yaml を修正（§2.1・§3）→ コミット・プッシュ → Blueprint を同期（§2.2）→ 再デプロイ → 2.3 の再観測で cwd/build_marker/app_list を確認する。
