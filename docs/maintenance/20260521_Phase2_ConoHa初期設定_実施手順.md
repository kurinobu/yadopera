# Phase 2: ConoHa 初期設定 — 実施手順（画面・コマンド単位）

**作成日**: 2026-05-21  
**親文書**: [ConoHa VPS 移転統合 引き継ぎ](./20260521_ConoHaVPS_移転統合_引き継ぎ.md)  
**サーバー**: `160.251.199.237`（Ubuntu 22.04.3 LTS・12GB）  
**状態**: ✅ **完了**（2026-05-21・必須 Step 0〜5 + Step 6 実質済み + Step 7 方針メモ済み）

---

## 本セッションの記録（2026-05-21・手順ナビの教訓）

実施自体は進んだが、**ナビ文書の誤り・確認不足**が複数あった。再発防止と引き継ぎ用に事実のみ記録する。

### インフラ実施結果（事実）

| Step | 結果 |
|------|------|
| 0 セキュリティグループ | `IPv4v6-SSH` + `IPv4v6-Web` + **`air-edison-admin-3000`**（`yadopera-dokploy-3000` は誤名のため差し替え） |
| 1 ホスト名 | `air-edison_VPS` |
| 2〜3 Dokploy | v0.29.4 導入・`http://160.251.199.237:3000` 管理画面 |
| 4 Postgres | `pgvector/pgvector:pg18`・`REPLICAS 1/1`・`vector 0.8.2` |
| 5 Redis | `redis:7`・`airedison-airedisonredis-eolvti`・`REPLICAS 1/1`・`redis-cli -a '…' PING` → **PONG** |

### 手順ナビで誤った／不足だった点（事実）

| 内容 | 正しいこと |
|------|------------|
| 左メニュー「Databases」 | **v0.29.4 には無い**。**Projects** → **+ Create Service** → **Database** |
| セキュリティグループ例 `yadopera-dokploy-3000` | **誤解を招く**。正本は **`air-edison-admin-3000`**（VPS ネームタグ準拠） |
| PG18 初回 Deploy | ボリューム **`/var/lib/postgresql/data`** のままだと **Exited (1)**。マウントは **`/var/lib/postgresql`** |
| コマンドの `<NAME>` プレースホルダ | **使わない**。`$(docker ps ...)` でコンテナ名を埋める |
| 「Redis に Docker image 欄がない」 | **誤り**。作成モーダルに **あり**（デフォルト `redis:7`） |
| Redis `redis-cli PING` のみ | パスワード設定時は **`NOAUTH`**。**`-a パスワード`** または Dokploy の Internal から確認 |

### 今後のナビ原則（本リポジトリ）

1. ユーザーが共有した **スクショ・コマンド出力を前提**に書く  
2. **プレースホルダを書かない**（コピペ1発）  
3. 未確認の UI は **推測で書かない**（「スクショください」）  
4. 誤記は本節と変更履歴に **訂正を残す**

---

## 完了条件（Phase 2 終了の定義）

| # | 項目 | 確認方法 |
|---|------|----------|
| 1 | Dokploy 管理画面 | ブラウザで `http://160.251.199.237:3000` にアクセスし、管理者アカウント作成済み |
| 2 | Postgres + pgvector | 空 DB で `CREATE EXTENSION vector;` が成功 |
| 3 | Redis | `redis-cli PING` → `PONG` |
| 4 | ファイアウォール | ConoHa で 22 / 80 / 443 / **3000** が許可（§ Step 0） |

**Phase 2 ではやらない**: ダンプ SCP・リストア、YadOPERA デプロイ、DNS 切替 → Phase 3〜5

---

## 実施順序（必ずこの順）

```
Step 0  ConoHa セキュリティグループ（80/443/3000）  ← 先にやる（未設定だと Dokploy が開けない）
Step 1  SSH 接続・ホスト名（任意）
Step 2  Dokploy インストール
Step 3  Dokploy 初回セットアップ（管理者アカウント）
Step 4  Postgres（pgvector/pg18）— Dokploy Database
Step 5  Redis — Dokploy Database
Step 6  動作確認の総括（vector・PING）— **Step 4・5 と同内容**（未実施ならここで実施）
Step 7  バックアップ方針メモ — **方針だけ今**。cron / S3 実装は **Phase 4 後**
```

**「5 で終わりか？」** — **必須の技術確認は Step 4（vector）+ Step 5（PONG）で完了**。Step 6 はその **整理・任意の一覧確認**。Step 7 は **運用メモ**（実装は後）。

---

## Step 0: ConoHa セキュリティグループ（最重要・先に実施）

Phase 1 で **`IPv4v6-SSH`**（port 22）のみ適用済み。Dokploy は **3000**、Traefik は **80 / 443** を使う。

### 0.0 ConoHa の用語（「Inbound」が無い理由）

| 他クラウドの用語 | ConoHa での対応 |
|------------------|-----------------|
| Inbound（受信許可） | ルール作成画面の **通信方向 = `IN`** |
| サーバー詳細のドロップダウン | **既製セキュリティグループを「付ける」だけ**（ポートを1つずつ入力しない） |

**サーバー詳細 → ネットワーク情報 → セキュリティグループ** では `Inbound` を検索しても出ません。  
ここでは **`IPv4v6-Web`** など **名前の付いたグループを追加** します。

| 既製グループ名 | 開くポート（公式） |
|----------------|-------------------|
| `IPv4v6-SSH` | 22 (TCP) — 適用済み |
| **`IPv4v6-Web`** | **80, 443 (TCP)** — **これを追加** |
| `IPv4v6-PostgreSQL` | 5432（Phase 2 では DB は Dokploy 内のみ・**付けない**） |

**3000** は既製に無い → **0.2 で独自グループを作成**（通信方向 `IN`）。

### 0.0.1 命名と 1 台集約（必読）

引き継ぎ [目標アーキテクチャ（1 台集約）](./20260521_ConoHaVPS_移転統合_引き継ぎ.md#目標アーキテクチャ1-台集約): **YadOPERA + InfluBerry + キャラまるわかり + 将来 PublishDone** を **同一 VPS** に載せる。

| 事実 | 説明 |
|------|------|
| セキュリティグループの単位 | **VPS 全体**（アプリごとではない） |
| InfluBerry 用に別グループ？ | **不要**（80/443 は `IPv4v6-Web`、管理は Dokploy :3000 の 1 つ） |
| **正本の独自グループ名** | **`air-edison-admin-3000`**（VPS ネームタグ `air-edison_VPS` の接頭辞 + `admin-3000`） |
| **使わない例** | `yadopera-dokploy-3000` 等 **単一アプリ名** |

**`yadopera-dokploy-3000` で既に作成している場合 → [Step 0.4](#04-誤ったグループ名の修正必須) を必ず実施**（名前を残すと同じ誤解が再発する）。

参照: [ConoHa セキュリティグループ仕様](https://doc.conoha.jp/products/vps-v3/security-v3/security-group-v3/)

### 0.1 サーバーに `IPv4v6-Web` を付ける（80 / 443）

いま開いている **サーバー詳細 → ネットワーク情報** のまま:

1. **セキュリティグループ** の **2 行目**（空いているドロップダウン）をクリック
2. 一覧から **`IPv4v6-Web`** を選択（`Inbound` ではなくこの名前）
3. 1 行目 **`IPv4v6-SSH`** はそのまま残す
4. まだ **保存しない**（3000 用グループを作ってからまとめて保存でも可）

### 0.2 ポート 3000 用の独自セキュリティグループを作る

1. 左メニュー **「セキュリティ」** → **「セキュリティグループ」**（サーバー詳細とは別画面）
2. **「セキュリティグループ作成」**（または「追加」）  
   - 名前（正本）: **`air-edison-admin-3000`**（ネームタグ `air-edison` に合わせる。アプリ名は入れない）
3. 作成したグループ名をクリック → **「＋」** でルール追加:

| 項目 | 値 |
|------|-----|
| **通信方向** | **`IN`**（＝外部からサーバーへ。Inbound 相当） |
| イーサタイプ | **IPv4** |
| プロトコル | **TCP** |
| ポート | **3000** |
| IP/CIDR | 自宅のグローバル IP（例 `203.0.113.45/32`）— 不明なら一時 **`0.0.0.0/0`**（全世界・後で絞る） |

4. **GitHub Auto Deploy 用** — 上記自宅 IP ルールに **加えて**、同グループに **もう 4 ルール**追加（2026-05-31 インシデントで必須と判明）:

| 通信方向 | イーサタイプ | プロトコル | ポート | IP/CIDR |
|----------|--------------|------------|--------|---------|
| **In** | **IPv4** | **TCP** | **3000** | `192.30.252.0/22` |
| **In** | **IPv4** | **TCP** | **3000** | `185.199.108.0/22` |
| **In** | **IPv4** | **TCP** | **3000** | `140.82.112.0/20` |
| **In** | **IPv4** | **TCP** | **3000** | `143.55.64.0/20` |

取得元: `GET https://api.github.com/meta` の **`hooks`** 配列（変更される場合あり・[GitHub Docs](https://docs.github.com/en/webhooks/testing-and-troubleshooting-webhooks/troubleshooting-webhooks#failed-to-connect-to-host)）。

**なぜ必要か**: Dokploy の GitHub App Webhook は `http://<VPS_IP>:3000/api/deploy/github` へ POST する。**port 3000 が自宅 IP のみ**だと GitHub 側は `failed to connect to host` となり、Autodeploy ON でも Deploy 走らない（[証跡](../evidence/20260531_dokploy_autodeploy_security_group_remediation.md)）。

5. IPv6 も使う場合は同様に **イーサタイプ IPv6** で `IN` / TCP / 3000 を **もう 1 ルール** 追加（GitHub hooks IPv6 は meta の `2a0a:a440::/29` 等 — 必要時のみ）
6. 一覧に戻り、グループが **作成済み** であることを確認

**自宅 IP の調べ方（Mac）**: ブラウザで「自分の IP」検索、または `curl -4 ifconfig.me`

### 0.3 サーバーに 3 グループを付けて保存

再び **サーバー詳細 → ネットワーク情報 → セキュリティグループ**:

| 行 | 付けるグループ |
|----|----------------|
| 1 | `IPv4v6-SSH` |
| 2 | `IPv4v6-Web` |
| 3 | **`air-edison-admin-3000` のみ**（`yadopera-*` のままにしない） |

右下 **「保存」** をクリック。

**注意**: `IPv4v6-SSH` / `IPv4v6-Web` など **ConoHa 既製グループはルール変更不可**。ポートを増やしたいときは **独自グループを新規作成** する。

### 0.4 誤ったグループ名の修正（必須）

**`yadopera-dokploy-3000` のまま残さない。** 運用・引き継ぎで「YadOPERA 専用」と誤解が再発する。

#### 方法 A: 名前の変更（画面に「セキュリティグループ名」編集がある場合）

1. **セキュリティ** → **セキュリティグループ** → **`yadopera-dokploy-3000`** を開く
2. **セキュリティグループ名** を **`air-edison-admin-3000`** に変更 → **保存**
3. サーバー詳細のドロップダウン表示も **`air-edison-admin-3000`** になっていることを確認

#### 方法 B: 作り直し（名前変更ができない場合・確実）

1. **新規作成** `air-edison-admin-3000`
2. **同じルールを 1 件だけ再登録**: `IN` / IPv4 / TCP / `3000` / 自宅 IP（My IP で可）
3. **サーバー詳細 → ネットワーク情報 → セキュリティグループ**（編集）  
   - 誤名グループを **削除**（×）  
   - 3 行目: **`air-edison-admin-3000`** を選択 → **保存**
4. **セキュリティグループ一覧**で誤名グループを **削除**（サーバーに未割当であること）

完了条件: サーバーに付いている 3 つが **`IPv4v6-SSH` / `IPv4v6-Web` / `air-edison-admin-3000`** のみ。`yadopera-*` が残っていない。

**実績（2026-05-21）**: スクショ確認済み — 上記 3 グループがサーバーに適用済み。

- [ ] 誤名グループを解消（リネームまたは B で作り直し）

### 0.5 確認（ローカル Mac から）

```bash
# 22（既に通っているはず）
nc -zv 160.251.199.237 22

# Step 0 完了後（Dokploy 導入前でも 3000 はまだ閉じている場合あり）
nc -zv 160.251.199.237 80
nc -zv 160.251.199.237 443
nc -zv 160.251.199.237 3000
```

- [x] Step 0 完了（3 グループ・**`air-edison-admin-3000`**・誤名なし）

---

## Step 1: SSH 接続・任意の初期整備

### 1.1 接続

```bash
ssh root@160.251.199.237
```

（root パスワードは Git 外のパスワード管理ツールから）

### 1.2 ホスト名（任意・引き継ぎどおり）

```bash
hostnamectl set-hostname air-edison_VPS
```

### 1.3 OS 内ファイアウォール（多くは inactive）

```bash
ufw status
```

`inactive` なら **Step 2 前に ufw は触らない**（ConoHa セキュリティグループが主因）。  
将来 `ufw enable` する場合は **22 を先に許可**してから 80/443/3000 を追加すること。

### 1.4 ポート占有確認（Dokploy インストール前必須）

```bash
ss -tlnp | grep -E ':80|:443|:3000' || echo "ports 80/443/3000 are free"
```

何か表示されたら、そのサービスを止めるか Dokploy インストールは失敗する（[公式](https://docs.dokploy.com/docs/core/installation)）。

- [ ] SSH ログイン成功
- [ ] 80 / 443 / 3000 が空いている

---

## Step 2: Dokploy インストール

サーバー上（root）で実行:

```bash
export ADVERTISE_ADDR=160.251.199.237
curl -sSL https://dokploy.com/install.sh | sh
```

- 所要: おおよそ **3〜7 分**（Docker 導入含む）
- 完了メッセージが出るまで待つ

### トラブル時

| 症状 | 対処 |
|------|------|
| ポート使用中 | `ss -tlnp` でプロセス特定・停止 |
| タイムアウト | Step 0 のセキュリティグループを再確認 |
| Docker エラー | `systemctl status docker`、ディスク `df -h`（100GB プラン） |

- [x] インストールスクリプト正常終了（v0.29.4・2026-05-21）

---

## Step 3: Dokploy 初回セットアップ（ブラウザ）

1. ブラウザで **`http://160.251.199.237:3000`** を開く
2. 管理者メール・パスワードを作成（**Git に書かない**。パスワード管理ツールへ）
3. ダッシュボードが表示されることを確認

※ HTTPS / ドメインは Phase 5 前でも可だが、**Phase 2 完了条件には含めない**（IP:3000 で十分）。

- [x] Dokploy 管理画面ログイン成功（2026-05-21）

---

## Step 4: Postgres（pgvector・PG18）

**理由**: staging ダンプ `yadopera_18pgvector_*.dump` は **PostgreSQL 18** 前提（引き継ぎ Phase 0）。

### 4.0 Dokploy v0.29 のメニュー（スクショ準拠）

左メニューに **「Databases」は無い**（v0.29.4）。DB は **Project → Environment → サービス追加** で作る。

| 左メニュー（共有スクショ） | 用途 |
|---------------------------|------|
| Home | ダッシュボード |
| **Projects** | **ここから DB / Redis を追加** |
| Deployments / Monitoring / … | 後続運用 |

### 4.1 プロジェクト作成（初回のみ）

1. 左メニュー **「Projects」**（Home の **「Go to projects ->」** でも可）
2. **「Create Project」**（または **+**）
3. 例:

| 項目 | 値 |
|------|-----|
| Project name | **`air-edison`**（VPS 共通インフラ。アプリ名 yadopera は入れない） |

4. 作成後、環境 **production**（デフォルト名のままで可）の画面を開く

### 4.2 PostgreSQL サービス追加（v0.29.4 スクショ準拠）

画面: **`air-edison / production`**（No services added yet）

1. **「Project Environment」** モーダルが開いていたら **閉じる**（DB 作成とは無関係。`PORT=3000` は触らない）
2. 右上 **「+ Create Service」** をクリック
3. メニュー **「Database」** をクリック（Application ではない）
4. 次の画面で **「PostgreSQL」** を選択  
   （一覧に出る **Select types…** から PostgreSQL を選んでも可）
3. 基本設定（**パスワードは強力なものを生成し Git 外に保存**）:

| 項目 | 推奨値 |
|------|--------|
| Name | `air-edison-postgres` |
| App Name | `air-edison-postgres` |
| Database Name | `postgres`（初期接続用・Phase 4 で `yadopera` 等を追加） |
| Database User | `yadopera_admin` |
| Database Password | （32文字以上推奨・手元メモ） |

4. **Docker image** フィールド: **あり**（作成モーダルに表示）→ `pgvector/pgvector:pg18` を入力

5. **Advanced → Volumes**（PG18 で必須・ここを誤ると `Exited (1)` で再起動ループ）  
   - マウント先は **`/var/lib/postgresql/data` ではなく `/var/lib/postgresql`**  
   - Dokploy のデフォルトが `.../data` のままだと、ログに  
     `Error: in 18+, these Docker images are configured to store database data in...`  
     と出て **REPLICAS 0/1** になる（[postgres#1259](https://github.com/docker-library/postgres/pull/1259)）

6. **Deploy** → **Confirm**

### 4.2 PG18 起動失敗の修正（いまの状態向け）

ログ: `Error: in 18+, ... data in: /var/lib/postgresql/data (unused mount/volume)` → **マウント先の修正 + 空ボリュームの削除**。

1. ブラウザ: **air-edison-postgres** → **Advanced** → **Volumes**  
   - マウントパスを **`/var/lib/postgresql`** に変更（末尾 `/data` を付けない）
2. **Advanced** → **Danger Zone** → データ削除（未リストアの空 DB のみ）
3. **General** → **Deploy** → **Confirm**
4. 手元 Mac ターミナル（`ssh root@160.251.199.237` 後）:

```bash
docker service ls | grep airedison
```

**`1/1`** になるまで待つ（`0/1` のままなら **Logs** と `docker service logs airedison-airedisonpostgres-wsxrdk --tail 30` を共有）。

### 4.3 vector 確認（手元ターミナル → SSH のみ）

```bash
PG=$(docker ps --format '{{.Names}}' | grep 'airedison-airedisonpostgres-wsxrdk' | head -1)
docker exec -it "$PG" psql -U postgres -d postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
docker exec -it "$PG" psql -U postgres -d postgres -c "SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';"
```

期待: `vector | 0.8.x` の 1 行。

`vector` 1 行で Step 4 完了。

- [x] Postgres デプロイ成功（`1/1`・2026-05-21）
- [x] `CREATE EXTENSION vector` 成功（`vector 0.8.2`）

**接続情報メモ（Phase 3/4 で使用・Git 外）**

- ホスト: Dokploy 表示の内部ホスト名（多くはサービス名ベース）または `160.251.199.237` + 公開ポート
- `DATABASE_URL` 形式（例）: `postgresql+asyncpg://yadopera_admin:PASSWORD@HOST:PORT/postgres`

---

## Step 5: Redis

**同じ画面** `air-edison / production` → **+ Create Service** → **Database** → **Redis**

### PostgreSQL との違い（v0.29.4・作成モーダル・スクショ準拠）

| 項目 | PostgreSQL（Step 4） | Redis（Step 5） |
|------|----------------------|-----------------|
| **Docker image 欄** | **あり** | **あり**（プレースホルダ `Default redis:7` 等） |
| 入力する値 | `pgvector/pgvector:pg18`（必須で上書き） | **空のまま**（デフォルト `redis:7` で可）または `redis:7.2-alpine` |
| タブ | Databases モーダルで PostgreSQL 選択 | 同モーダルで **Redis** タブを選択 |

**過去の誤記**: 「Redis に Docker image 欄がない」は **誤り**。両方とも作成モーダルに欄がある。

### 5.0 入力項目（スクショどおり）

| 項目 | 推奨値 |
|------|--------|
| Name | `air-edison-redis` |
| App Name | 自動（例: `airedison-airedisonredis`）で可 |
| Database Password | 強力なパスワード（Git 外に保存） |
| **Docker image** | **あり** — そのまま（`redis:7` デフォルト）で Phase 2 は可。揃えるなら `redis:7.2-alpine` |

1. **Create** → **Deploy** → **Confirm**

3. 手元 Mac ターミナル（`ssh root@160.251.199.237` 済み）で確認:

```bash
docker service ls | grep airedison
```

`air-edison-redis` 相当の行が **`1/1`** であること。

### 5.1 PING 確認（SSH・コピペ可）

作成時に **Database Password** を設定している場合、`PING` だけでは **`NOAUTH Authentication required.`** になる（正常）。

1. ブラウザ: **air-edison-redis** → **General** → **Internal** の Password を確認（Git に書かない）
2. SSH で — **Dokploy Internal のパスワードを `-a` の引用符内に入れる**（文字列 `YOUR_REDIS_PASSWORD` をそのまま打たら `WRONGPASS` になる）:

```bash
REDIS=$(docker ps --format '{{.Names}}' | grep airedison | grep -i redis | head -1)
echo "Redis container: $REDIS"
docker exec -it "$REDIS" redis-cli -a '（Internalのパスワード）' PING
```

期待: `PONG`（`Warning: Using password with -a` は無視してよい）

**注意**: パスワードをチャット・スクショ・Git に載せない。シェル履歴に残るため、必要なら Phase 3 前に Redis パスワードを Dokploy 上で再生成可。

- [x] Redis デプロイ成功（`1/1`・2026-05-21）
- [x] `PING` → `PONG`（要 `-a` パスワード。Dokploy Internal と一致すること）

**接続情報メモ（Git 外）**

- `REDIS_URL=redis://HOST:PORT/0`

---

## Step 6: 動作確認の総括（vector・PING）

### 必須（Phase 2 完了条件に含む）

| 確認 | 実施 Step | あなたの実績（2026-05-21） |
|------|-----------|---------------------------|
| `CREATE EXTENSION vector` | **Step 4.3** | ✅ `vector 0.8.2` |
| Redis `PONG`（`-a` パスワード） | **Step 5.1** | ✅ `PONG` |

→ **Step 6 の必須部分は既に完了**（Step 4・5 で実施済み）。

### 任意（推奨・1 分）

SSH（手元ターミナル → `ssh` 済み）で一覧だけ確認:

```bash
docker service ls | grep airedison
docker ps --format 'table {{.Names}}\t{{.Status}}' | grep -E 'airedison|dokploy|traefik'
```

Postgres / Redis が **Up**、`REPLICAS 1/1` なら Step 6 完了扱いでよい。

- [x] vector・PING 確認（Step 4・5 で実施済み）
- [ ] 任意: 上記 `docker ps` 一覧（未実施でも Phase 2 必須条件は満たしている）

---

## Step 7: バックアップ方針（メモ・cron は Phase 4 後）

**今やること**: 方針を決めて **Git 外の手元メモ**（または下表を参照）。**やらないこと**: cron 設定・S3 バケット作成・初回 `pg_dump`（データ未リストアのため Phase 4 後）。

| 対象 | Phase 2（方針のみ） | Phase 4 以降（実装） |
|------|---------------------|----------------------|
| **Postgres**（`air-edison-postgres`） | Dokploy **Backups** タブで S3 先を検討 | リストア後、**日次** `pg_dump`（Dokploy Backups または cron + 手元 SCP） |
| **Redis**（`air-edison-redis`） | 空再開可・**バックアップ優先度低** | 本番運用安定後に RDB 方針を検討 |
| **Dokploy 本体** | 設定は画面のみ・要エクスポート検討 | アップデート前にバージョン確認 |
| **証跡** | — | 実施記録は `docs/evidence/`（任意） |

参照: [Dokploy Backups](https://docs.dokploy.com/docs/core/databases/backups)

- [x] バックアップ方針メモ（本節・2026-05-21。cron 実装は Phase 4 後）

---

## Phase 2 完了チェックリスト

- [x] Step 0: ConoHa で 80 / 443 / 3000（+22）許可
- [x] Step 2: Dokploy インストール完了（v0.29.4）
- [x] Step 3: 管理者アカウント作成・画面アクセス
- [x] Step 4: `pgvector/pgvector:pg18` + `vector 0.8.2`
- [x] Step 5: Redis `PONG`（パスワード付き `-a`）
- [x] Step 6: vector・PING（Step 4・5 で実施済み）
- [x] Step 7: バックアップ方針メモ（cron は Phase 4 後）
- [ ] 接続情報（Postgres / Redis パスワード・Internal URL）を **Git 外**に保存 — Phase 3 前に推奨

**次**: 親文書 **Phase 3** ✅ 完了（2026-05-22）→ **Phase 4** [DB リストア](./20260521_Phase4_DBリストア_実施手順.md)

---

## 次会話用プロンプト（Phase 2 途中再開）

```
Phase 2 の続き。docs/maintenance/20260521_Phase2_ConoHa初期設定_実施手順.md の
Step X から。実施結果: （例: Step 0 完了、Dokploy インストール中）
```

---

## 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-05-21 | 初版（Phase 2 開始） |
| 2026-05-21 | §0.0.1 追記: 1 台集約・セキュリティグループは VPS 共通・中立命名 |
| 2026-05-21 | §0.4 追加: 誤名 `yadopera-dokploy-3000` の修正は必須 |
| 2026-05-21 | 正本名 **`air-edison-admin-3000`**（ネームタグ準拠）・Step 0 実績反映 |
| 2026-05-21 | Step 4〜5: v0.29 は左メニュー Databases なし → **Projects** 経由に修正 |
| 2026-05-21 | Step 5: Redis に Docker image 欄なしと誤記 → **両方あり** に訂正 |
| 2026-05-21 | §本セッションの記録 追加・Redis NOAUTH と `-a` 手順 |
| 2026-05-21 | Phase 2 完了（Postgres 1/1・Redis PONG） |
