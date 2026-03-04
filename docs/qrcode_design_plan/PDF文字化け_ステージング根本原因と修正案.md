# PDF文字化け ステージング根本原因と修正案

**作成日**: 2026年3月4日  
**緊急度**: 🔴 **最高（PoC実行中・顧客使用中）**  
**状態**: 原因確定・修正案提示（**指示があるまで修正しない**）

---

## 1. 事実の整理

### 1.1 revert 後もステージングで文字化けが続いている

- コミット `a081c53`（d7d700c の revert）をステージングにデプロイ済み。
- デプロイ後・サイトデータ消去・強制リロード後も、ステージングで取得した PDF は **日本語が文字化けしたまま**。

### 1.2 対象 PDF のフォント確認

| ファイル | 埋め込みフォント | 判定 |
|----------|------------------|------|
| `qrcode-room-1772614373.pdf`（revert 後・ステージング取得） | **`/AAAAAA+DejaVuSans`**, `/Helvetica`, `/Helvetica-Bold` | ❌ **日本語フォントなし**。DejaVu のみで日本語は豆腐化。 |

- **IPA ゴシック（ipagp）は一切使われていない** → ステージングのコンテナ内で、コードが参照している **IPA の固定パスがすべて存在していない** と判断できる。
- 固定パスリストの **5 番目** の `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` だけが存在し、そこで登録が止まっている。

### 1.3 現在の設定（revert 後の develop）

- **render.yaml**: `dockerfilePath: ./backend/Dockerfile`, `dockerContext: ./backend` → **Dockerfile は使用されている**。
- **backend/Dockerfile**: `fonts-dejavu`, `fonts-noto-cjk`, `fonts-ipafont`, `fonts-ipafont-gothic` を `apt-get install` でインストール。
- **qr_code_service.py**: 次の固定パスを先頭から順に参照。
  1. `/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf`
  2. `/usr/share/fonts/truetype/ipafont-gothic/ipagp.ttf`
  3. `/usr/share/fonts/truetype/ipafont/ipagp.ttf`
  4. `/usr/share/fonts/truetype/ipafont/ipag.ttf`
  5. `/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf` ← **ここだけ存在 → DejaVu が採用 → 文字化け**

---

## 2. 根本原因の確定

### 2.1 結論

**Render 上でビルドされた Docker イメージ内に、IPA ゴシックの「期待しているパス」が存在していない。**

- ローカルで同じ Dockerfile からビルドしたイメージでは、ステップ1で  
  `/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf` が存在することを確認済み。
- 一方、ステージングで生成された PDF は **DejaVu のみ** のため、**Render のビルド結果では 1〜4 番目のパスがすべて存在していない**。

### 2.2 想定される要因（優先度順）

#### 要因A: Render のビルドキャッシュ

- 過去に **Dockerfile にフォントを追加する前のレイヤー** がキャッシュされており、`RUN apt-get install ... fonts-ipafont-gothic` が実行されていない（または古いレイヤーが使われている）可能性。
- その場合、コンテナ内に `/usr/share/fonts/opentype/ipafont-gothic/` が存在せず、固定パス 1〜4 はすべて失敗し、5 番目の DejaVu だけがヒットする。

#### 要因B: ベースイメージ・パッケージの差

- `python:3.11-slim` のタグが指すイメージや、Render のリージョン・キャッシュの関係で、ローカルと異なるレイヤーが使われている可能性。
- Debian の公式では `fonts-ipafont-gothic` は  
  `/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf` に置かれるが、**そのレイヤーが Render 側で実行されていなければフォントは存在しない**。

#### 要因C: 過去の「env: python」運用の名残

- 以前は `render.yaml` で `env: python` により **Dockerfile 未使用** だった（PDF文字化け問題_緊急調査分析_修正案.md の通り）。
- 現在は `dockerfilePath` / `dockerContext` に切り替わっているが、**サービス作成時やキャッシュの都合で、古いビルド結果が残っている**可能性は否定できない。

---

## 3. 大原則の確認

1. **Fundamental solution > Provisional solution**: 根本対策を優先する。
2. **Simple structure > Complex structure**: シンプルな構造を優先する。
3. **Unification**: ローカル・ステージングで同じ Dockerfile・同じロジックで動かす。
4. **Concrete > General**: 具体的なパス・手順を明示する。
5. **Safe and reliable**: キャッシュや環境差に左右されず、確実に日本語フォントが使えるようにする。
6. **Docker environment is mandatory**: 本番・ステージングとも Docker 前提。

---

## 4. 修正案（大原則準拠）

### 4.1 方針: 「アプリ側で確実に参照できるパス」を Dockerfile で用意する

- **目的**: システムの `apt` のインストール先に依存せず、**Docker ビルド時に IPA ゴシックを必ず「決まったパス」にコピー**し、コードからはそのパスだけを最優先で参照する。
- **効果**:
  - キャッシュで `apt-get install` がスキップされていても、**コピー用の RUN を新設すればそのレイヤーはキャッシュされず**、フォントが入った状態でイメージが作られる（またはコピー失敗でビルドが落ち、問題に気づける）。
  - コードは「まず /app 以下の確定パス」を見るため、**Render とローカルで同じ挙動**にできる。

### 4.2 修正案A: Dockerfile でフォントを /app にコピーし、コードで最優先参照（推奨）

#### Dockerfile の変更

- 既存の `RUN apt-get update && apt-get install -y ... fonts-ipafont-gothic ...` の**直後**に、**同じ RUN の続き**で以下を追加する（レイヤーを分けない方が、キャッシュ抜けで確実）。
  - `/app/fonts` を作成し、`/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf` を `/app/fonts/ipagp.ttf` にコピーする。

例（要約）:

```dockerfile
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    fonts-dejavu \
    fonts-noto-cjk \
    fonts-ipafont \
    fonts-ipafont-gothic \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/fonts \
    && cp /usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf /app/fonts/
```

- `cp` が失敗すればビルドが失敗するため、**フォントが入っていないイメージがデプロイされる事態を防げる**。

#### qr_code_service.py の変更

- PDF 用日本語フォントの **候補パスリストの先頭** に、`/app/fonts/ipagp.ttf` を追加する。
- それ以外の既存の固定パス（opentype / truetype の IPA・DejaVu）は、そのまま「フォールバック」として並べる。

例（先頭だけ）:

```python
japanese_font_paths = [
    "/app/fonts/ipagp.ttf",  # Dockerfile でコピーした確定パス（最優先）
    "/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf",
    # ... 既存の 2〜5 番目をそのまま
]
```

- これにより、**Render でビルドしたイメージでは必ず 1 番目のパスが存在**し、ステージングでも IPA が使われ、PDF の文字化けが解消される。

### 4.3 修正案B: Render でキャッシュなし再ビルド（補足）

- **運用で可能なら**: Render のダッシュボードで「Clear build cache」等を実行し、**キャッシュを使わずにフルビルド**する。
- これで「要因A: キャッシュで apt が実行されていない」が解消され、`/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf` が存在する可能性はある。
- ただし **キャッシュの有無は環境依存**のため、**確実性では修正案Aに劣る**。修正案Aを実施したうえで、必要に応じてキャッシュクリアも行うのがよい。

### 4.4 修正案C: フォントをリポジトリに同梱する（代替）

- `backend/fonts/ipagp.ttf` 等をリポジトリに置き、コードからは `os.path.join(app_root, "fonts", "ipagp.ttf")` のように参照する。
- ライセンス確認が必要であり、リポジトリ肥大化にもなるため、**まずは修正案Aを推奨**する。

---

## 5. 推奨実施順序（修正案Aを採用する場合）

1. **バックアップ**: 現状の `backend/Dockerfile` と `backend/app/services/qr_code_service.py` をバックアップする。
2. **Dockerfile**: 上記のとおり、`RUN apt-get install ...` の末尾に `mkdir -p /app/fonts` と `cp ... ipagp.ttf /app/fonts/` を追加する。
3. **qr_code_service.py**: `japanese_font_paths` の先頭に `"/app/fonts/ipagp.ttf"` を追加する。
4. **ローカル**: 同じ Dockerfile で `docker build` し、コンテナ内で `ls -la /app/fonts/ipagp.ttf` と PDF 生成を確認する。
5. **コミット・プッシュ**: develop にコミット・プッシュし、ステージングの自動デプロイを待つ。
6. **ステージング**: デプロイ完了後、PDF を再度取得し、埋め込みフォントに IPA ゴシック（または IPAPGothic）が含まれること・日本語が正しく表示されることを確認する。

---

## 6. まとめ

| 項目 | 内容 |
|------|------|
| **原因** | ステージングの Docker イメージ内に、コードが参照する IPA のパス（1〜4 番目）が存在しておらず、5 番目の DejaVu のみが使われている。その結果、PDF に日本語フォントが埋め込まれず文字化けしている。 |
| **要因** | Render のビルドキャッシュ等により、`apt-get install fonts-ipafont-gothic` が効いていない、またはイメージ差でパスが一致していない可能性が高い。 |
| **修正方針** | Dockerfile で IPA ゴシックを **必ず** `/app/fonts/ipagp.ttf` にコピーし、コードではそのパスを **最優先** で参照する。これで環境差・キャッシュに依存せずステージングでも日本語表示を実現する。 |
| **大原則** | 確実性（Safe and reliable）と、ローカル・ステージングの同一挙動（Unification）を満たすため、**修正案A（/app/fonts へのコピー＋先頭参照）を推奨**する。 |

---

## 7. 実施記録（2026-03-04）

- **バックアップ**: `backups/20260304_pdf_font_app_fonts_fix/`（Dockerfile, qr_code_service.py）
- **実施内容**: 上記「修正案A」を適用。Dockerfile で `/app/fonts/ipagp.ttf` を用意し、qr_code_service.py の `japanese_font_paths` の先頭に同パスを追加済み。
- **次の確認**: ローカルで `docker build` → PDF 生成テスト。問題なければ develop にコミット・プッシュし、ステージングで PDF の日本語表示を確認する。
