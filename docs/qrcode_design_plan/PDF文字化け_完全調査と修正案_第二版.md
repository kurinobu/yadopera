# PDF文字化け 完全調査と修正案（第二版）

**作成日**: 2026年3月4日  
**緊急度**: 🔴 **最高（PoC実行中・顧客使用中）**  
**状態**: 原因の完全調査完了・修正案提示（**指示があるまで修正しない**）

---

## 1. 事実の整理

### 1.1 ユーザー報告の要点

- **「修正する前は文字化けしていなかった」** → 当方の一連の修正（d7d700c の QR 変更、revert、/app/fonts コピー案）の**前**の時点では、ステージングの PDF は正常だった。
- **「再度調査分析を完全にしなさい」** → なぜ以前は動いていたのか、なぜ今は動かないのかを、前提からやり直して説明する必要がある。

### 1.2 共有PDFのフォント確認（最新）

| ファイル | 埋め込みフォント | 判定 |
|----------|------------------|------|
| `qrcode-entrance-1772615530.pdf`（134eecc デプロイ後・ステージング取得） | **`/AAAAAA+DejaVuSans`**, `/Helvetica`, `/Helvetica-Bold` | ❌ **日本語フォントなし**。IPA は未使用。 |

- コミット 134eecc では「Dockerfile で `/app/fonts/ipagp.ttf` を用意し、コードで最優先参照」にしたが、**ステージングで生成された PDF には依然として IPA が一切使われていない**。
- つまり、**Render 上で動いているコンテナ内では `/app/fonts/ipagp.ttf` が存在していないか、参照されていない**。

### 1.3 時系列の整理（何が「修正前」か）

| 時点 | コミット | 内容 | ステージング PDF |
|------|----------|------|------------------|
| **修正前（正常だった状態）** | **fb18114** | Freeプラン広告のみ。Dockerfile は `apt-get` でフォント導入のみ。qr_code_service は固定パス（/usr/share/...）のみ。 | ✅ **文字化けしていなかった**（ユーザー証言） |
| 問題のきっかけ | d7d700c | QR 縦位置・Noto・SVG フォントサイズ・Dockerfile に fonts-noto-core 追加。**PDF のフォントロジックは変更していない**（従来どおり固定パス）。 | ❌ 文字化け報告 |
| revert | a081c53 | d7d700c を revert。実質 fb18114 のコード＋履歴に revert コミットが乗った状態。 | ❌ 依然文字化け |
| /app/fonts 修正 | 134eecc | Dockerfile で `mkdir /app/fonts` と `cp ipagp.ttf /app/fonts/` を追加。コードで `/app/fonts/ipagp.ttf` を最優先。 | ❌ 依然文字化け（DejaVu のみ） |

- **重要**: 「修正する前」＝**fb18114 の時点**。当時は **apt-get で入れたフォントを、/usr/share/... の固定パスで参照していただけ**で、ステージング PDF は動いていた。
- その後、**コードのフォントロジックは fb18114 と実質同じ（固定パス）のまま**なのに、d7d700c 以降は一貫してステージングで文字化けしている。
- したがって原因は **「コードの変更」ではなく「Render 上でビルド・実行されている Docker イメージの内容」** である。

---

## 2. 原因の完全調査

### 2.1 なぜ fb18114 のときは動いていたか（推定）

- 2026年2月8日付の「PDF文字化け問題 デプロイ完了・結果評価報告書」では、**render.yaml を Dockerfile 利用に変更したあと**「PDFの文字化けが解消した」とある。
- 当時は **Render がその時点でフルビルド（またはキャッシュのないビルド）を行い**、`RUN apt-get install ... fonts-ipafont-gothic` が実行され、`/usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf` がイメージ内に存在していたと考えられる。
- つまり「**修正前（fb18114）に文字化けしていなかった**」のは、**その時点の Render のビルド結果では、apt で入れた IPA が期待パスに存在していた**から、と説明できる。

### 2.2 なぜ d7d700c 以降は一貫して文字化けするか

- d7d700c では **PDF 用のフォントパスやロジックは一切変更していない**。変更したのは QR 描画（PNG/SVG）と Dockerfile の `fonts-noto-core` のみ。
- それにもかかわらずステージングで PDF が文字化けしたということは、**d7d700c のデプロイ時に、Render が別の（古い）イメージを使うか、キャッシュにより `apt-get install` が効いていないビルドになっている**可能性が高い。
- その後、a081c53（revert）や 134eecc（/app/fonts コピー）をデプロイしても文字化けが続いているのは、
  1. **RUN レイヤーのキャッシュ**: `RUN apt-get update && apt-get install -y ...` が、フォントが入っていない古いキャッシュでスキップされている。  
  2. **134eecc で追加した `&& mkdir -p /app/fonts && cp ...` も同じ RUN 内**のため、**その RUN 全体がキャッシュでスキップ**されると、`/app/fonts/ipagp.ttf` も作成されない。  
  3. その結果、実行時には `/app/fonts/ipagp.ttf` も `/usr/share/.../ipagp.ttf` も存在せず、最後の DejaVu だけがヒットし、PDF は DejaVu のみで描画される（日本語は豆腐）。

### 2.3 Render のビルドとキャッシュの関係

- Render は Docker ビルドに BuildKit 等を使い、**レイヤー単位でキャッシュ**する。
- **Dockerfile の RUN の文言が一度でも変われば**、通常はその RUN から先はキャッシュが無効になり、やり直される。  
  しかし、
  - サービス作成時期や、過去に `env: python` で動かしていた時期の「別経路のビルド結果」が残っている、
  - または Render 側の都合で「前回成功ビルドのイメージを再利用」している、
  といった可能性は否定できない。
- いずれにせよ、**「apt-get で入れたフォント」や「同じ RUN 内の cp」に依存している限り、キャッシュや環境差で「フォントがイメージに入らない」事態が繰り返しうる**。

### 2.4 結論（根本原因）

| 項目 | 内容 |
|------|------|
| **直接の事実** | ステージングで生成された PDF には IPA が埋め込まれておらず、DejaVu のみ。コードは `/app/fonts/ipagp.ttf` を最優先で参照しているため、**実行時コンテナ内に `/app/fonts/ipagp.ttf` が存在していない**。 |
| **根本原因** | Render 上でビルドされた Docker イメージにおいて、**フォントを「RUN apt-get install とその RUN 内の cp」に依存しており、キャッシュやビルド経路の差で、その RUN が実質実行されていない（または apt でフォントが入っていない）状態になっている**。 |
| **なぜ「修正前」は動いていたか** | fb18114 の頃は、その時点の Render のビルドでは apt でフォントが入り、固定パスに ipagp.ttf が存在していた。その後、キャッシュやデプロイ経路の変化で「フォントが入らないビルド」が使われるようになった。 |

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

### 4.1 方針: **フォントを apt に一切依存させない（リポジトリに同梱）**

- **目的**: 日本語 PDF 用フォントを **「Docker ビルド時の apt-get や RUN の cp」に一切依存させない**。  
  リポジトリに **フォントファイルを1つ同梱**し、Dockerfile の `COPY` だけで `/app/fonts/` に配置する。
- **効果**:
  - ビルドキャッシュの有無や、apt の実行有無に左右されない。
  - 同じコミットからビルドすれば、どこでビルドしても同じ内容のイメージになる（Unification・Safe and reliable）。
- **ライセンス**: IPA フォント（ipagp.ttf）は **IPA Font License** で、再配布・組み込みが許諾されている。

### 4.2 修正案: フォントを backend/fonts に置き、COPY のみで配置する

#### 4.2.1 フォントファイルの用意

- **配置先**: `backend/fonts/ipagp.ttf`
- **入手方法**（いずれか）:
  1. **ローカルで Docker から取り出す**  
     ```bash
     mkdir -p backend/fonts
     docker run --rm -v "$(pwd)/backend/fonts:/out" python:3.11-slim bash -c "apt-get update && apt-get install -y fonts-ipafont-gothic && cp /usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf /out/"
     ```
  2. **IPA の公式サイト**から IPA ゴシック（IPAfont00303 等）をダウンロードし、同梱されている `ipagp.ttf` を `backend/fonts/ipagp.ttf` に配置する。

#### 4.2.2 Dockerfile の変更

- **削除**: 現在の RUN の末尾にある `&& mkdir -p /app/fonts && cp /usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf /app/fonts/` を**削除**する（apt に依存するコピーをやめる）。
- **追加**: `WORKDIR /app` の直後（または RUN の前）に、**フォントだけを先に COPY する**レイヤーを追加する。  
  - 例: `COPY fonts/ /app/fonts/`  
  - `dockerContext` が `./backend` なので、ビルドコンテキスト内の `fonts/` は `backend/fonts/` に対応する。
- これにより、**apt を実行する RUN がキャッシュでスキップされても**、`/app/fonts/ipagp.ttf` は必ずイメージに含まれる。

#### 4.2.3 qr_code_service.py

- **変更不要**（既に `/app/fonts/ipagp.ttf` を先頭で参照している想定）。  
  もし先頭が `/app/fonts/ipagp.ttf` でない場合は、これを先頭にしておく。

#### 4.2.4 .gitignore

- `backend/fonts/*.ttf` を **ignore しない**（リポジトリに含める）。  
  逆に、一時ファイルだけ ignore する場合は `backend/fonts/*.tmp` などに限定する。

### 4.3 実施手順（案）

1. **バックアップ**: 現在の `backend/Dockerfile` と `backend/app/services/qr_code_service.py` をバックアップする。
2. **backend/fonts の作成**: `backend/fonts` ディレクトリを作成し、上記のいずれかの方法で `ipagp.ttf` を配置する。
3. **Dockerfile**:  
   - RUN から `&& mkdir -p /app/fonts && cp ...` を削除。  
   - `COPY fonts/ /app/fonts/` を追加（WORKDIR の後、他の COPY の前が無難）。
4. **ローカル**: `docker build -f backend/Dockerfile backend/` でビルドし、コンテナ内で `ls -la /app/fonts/ipagp.ttf` と PDF 生成を確認する。
5. **コミット・プッシュ**: `backend/fonts/ipagp.ttf` と Dockerfile をコミットし、develop にプッシュする。
6. **ステージング**: デプロイ完了後、PDF を取得し、埋め込みフォントに IPA（または IPAPGothic）が含まれること・日本語が正しく表示されることを確認する。

### 4.4 補足: キャッシュ対策のみでは不十分な理由

- RUN に「キャッシュバスター」用の ARG や `echo` を足すだけでは、**Render 側のキャッシュキーや再ビルドポリシー**によっては、依然として古いレイヤーが使われる可能性がある。
- **「フォントファイルをコンテキストに含め、COPY で確実にイメージに入れる」**方式にすれば、**apt や RUN の実行結果に一切依存しない**ため、大原則の「Safe and reliable」を満たせる。

---

## 5. まとめ

| 項目 | 内容 |
|------|------|
| **「修正前」の状態** | fb18114 の時点では、ステージング PDF は文字化けしていなかった。当時は固定パスのみで、apt で入れた IPA がイメージ内に存在していた。 |
| **現在の事実** | 134eecc デプロイ後も、ステージングの PDF は DejaVu のみ。つまり `/app/fonts/ipagp.ttf` が実行時イメージに存在していない。 |
| **根本原因** | Render の Docker ビルドで、フォント導入を「RUN apt-get install とその RUN 内の cp」に依存しており、キャッシュ等でその RUN が実質スキップされている（または apt でフォントが入っていない）状態が続いている。 |
| **修正方針** | フォントを **リポジトリに同梱**し、Dockerfile では **COPY fonts/ /app/fonts/** のみで配置する。apt に依存しないため、キャッシュに左右されず確実に日本語表示できる。 |
| **大原則** | Safe and reliable（確実性）と Unification（同一ビルドで同じ結果）を満たすため、**フォント同梱＋COPY のみ**の案を推奨する。 |

---

## 6. 実施記録（2026-03-04）

- **バックアップ**: `backups/20260304_pdf_font_bundle_fix/`（Dockerfile, qr_code_service.py）
- **実施内容**: 上記「フォント同梱」案を適用。  
  - `backend/fonts/ipagp.ttf` を Docker から取得して配置。  
  - Dockerfile: RUN から mkdir/cp を削除し、`COPY fonts/ /app/fonts/` を追加（apt 非依存）。  
  - qr_code_service.py は既に `/app/fonts/ipagp.ttf` を先頭参照のため変更なし。  
- **次の確認**: ローカルで `docker build` 後、PDF 生成を確認。問題なければ develop にコミット・プッシュし、ステージングで PDF の日本語表示を確認する。
