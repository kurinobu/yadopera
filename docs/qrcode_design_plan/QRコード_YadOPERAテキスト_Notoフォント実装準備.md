# QRコード「YadOPERA」テキスト — Notoフォント実装準備

**作成日**: 2026年3月4日  
**最終更新日**: 2026年3月4日  
**目的**: Notoフォント（モダン・スッキリしたデザイン）導入の経緯整理・失敗事例の確認・実装準備。

**実施状況**: A実装（縦位置上下中央）・B実装（Notoフォント）を実施済み。実施記録は `QRコード_縦位置とNoto_実施記録_20260304.md` を参照。

---

## 1. Noto関連の実装経歴・失敗事例（文書調査結果）

### 1.1 既に導入済みのNoto（PDF日本語用）

| 項目 | 内容 |
|------|------|
| **パッケージ** | `fonts-noto-cjk`（Dockerfileに記載済み） |
| **用途** | PDF内の**日本語**（施設名・設置場所・生成日時）用として検討された |
| **結果** | **PDFでは未使用**。理由は下記「失敗事例」参照 |

### 1.2 失敗事例・制限（必ず遵守すること）

| 文書 | 内容 |
|------|------|
| **QRコードデザイン変更_ブラウザテスト結果_完全調査分析_修正案.md** | Noto Sans CJK（`.ttc`）は **reportlab で直接使用できない**（"PostScript outlines are not supported"）。PDF用日本語は **IPAゴシック（.ttf）** で対応済み。 |
| **同・修正案** | フォントパスは IPA を優先し、Noto CJK は TTC のため reportlab 登録から除外。 |
| **PDF文字化け問題_緊急調査分析_修正案.md** | Render.com で `env: python` のときは Dockerfile が使われずフォントが入らない問題。**現状は Dockerfile でビルドしている前提**で、IPA/DejaVu のパスを opentype に合わせて修正済み。 |

**結論（Noto利用のルール）**

- **reportlab（PDF）**: **TTC は使用不可**。使用するのは **.ttf のみ**。
- **Pillow（PNG）**: `.ttf` を指定すれば Noto 利用可能（TTC は環境によっては Pillow で読めるが、本番では .ttf に統一する方が安全）。
- **QRコード中央の「YadOPERA」**: ラテンのみなので **Noto Sans（Latin）** の **.ttf** を使う。Noto CJK（.ttc）は使わない。

### 1.3 今回の対象（Noto Sans Latin — QR用「YadOPERA」）

| 項目 | 内容 |
|------|------|
| **用途** | QRコード中央の「YadOPERA」テキスト（PNG/PDF/SVG）のフォントを **モダン・スッキリ** にしたい |
| **現状** | `DejaVuSans-Bold.ttf`（`/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf`） |
| **希望** | Noto 系でよりモダンな見た目にしたい |
| **対象形式** | PNG（PIL）、PDF（QR画像部分はPILで描画した画像を貼り付け）、SVG（`font-family` のみ。サーバーにNotoが入っていれば参照可能） |

**Noto CJK は今回の「YadOPERA」テキストには使わない**（CJKは日本語等用であり、かつ .ttc のため reportlab では使えない）。

---

## 2. Noto Sans（Latin）の利用方法

### 2.1 パッケージとパス（Debian / python:3.11-slim 前提）

| 項目 | 内容 |
|------|------|
| **パッケージ** | `fonts-noto-core`（Debian/Ubuntu） |
| **インストール後パス例** | `/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf`（要：Docker内で確認） |
| **フォント名** | Noto Sans（Latin）。Bold で「YadOPERA」を描画。 |
| **ファイル形式** | **.ttf** のため、PIL および reportlab の TTFont で使用可能（TTC 問題なし）。 |

- **注意**: `fonts-noto-cjk` は既に入れてあるが、CJK は「YadOPERA」には不要。**QR中央テキスト用**には `fonts-noto-core` を追加する。
- **サイズ**: fonts-noto-core はインストール後おおよそ 40MB 以上。Docker イメージ肥大化を許容できるか確認すること。

### 2.2 Dockerfile の変更案（指示があるまで実施しない）

```dockerfile
# 追加するパッケージ（1行で追加）
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    fonts-dejavu \
    fonts-noto-core \
    fonts-noto-cjk \
    fonts-ipafont \
    fonts-ipafont-gothic \
    && rm -rf /var/lib/apt/lists/*
```

- `fonts-noto-core` を **fonts-noto-cjk の前か後** に1行追加。
- 既存の `fonts-noto-cjk` は PDF 日本語用のフォント検索には使っていないが、他機能で参照している可能性があるため残す。

### 2.3 コード側の変更案（指示があるまで実施しない）

**対象ファイル**: `backend/app/services/qr_code_service.py`

- **PNG・PDF**（QR画像に「YadOPERA」を描画している箇所）  
  - 使用フォントを **DejaVu Sans Bold** から **Noto Sans Bold** に切り替える。  
  - フォントパスを、Docker 内で確認した **.ttf** のパスに変更（例: `/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf`）。  
  - フォールバックは従来どおり「フォントが見つからない場合は DejaVu Sans Bold または load_default()」とする。
- **SVG**  
  - `font-family` を `"Noto Sans", sans-serif` などに変更（Noto Sans がサーバーにインストールされていればブラウザが参照可能。インストールされていない環境では sans-serif にフォールバック）。

**実装時の注意**

- フォントパスは **必ず Docker イメージ内で存在確認**すること（`docker run --rm ... ls /usr/share/fonts/truetype/noto/` 等）。
- reportlab では **TTC を登録しない**（既存の IPA 優先ロジックを維持）。今回追加するのは **Noto Sans（Latin）.ttf** のみで、PDF の日本語には引き続き IPA を使用する。

---

## 3. 失敗を防ぐためのチェックリスト（実装時）

- [ ] **TTC を reportlab に渡していない**（PDF 日本語は IPA の .ttf のみ）
- [ ] **QR用「YadOPERA」** には **Noto Sans Bold の .ttf** のみを指定（PIL / 画像経由で PDF に貼り付け）
- [ ] Dockerfile に `fonts-noto-core` を追加したうえで、コンテナ内で `NotoSans-Bold.ttf` の存在を確認済み
- [ ] フォント読み込み失敗時は従来どおり DejaVu または load_default() にフォールバック
- [ ] 大原則に従い、**Docker 環境でビルド・動作確認**してからステージングデプロイを検討

---

## 4. 参照した文書

| 文書 | 利用した内容 |
|------|----------------|
| docs/qrcode_design_plan/QRコードデザイン変更_ブラウザテスト結果_完全調査分析_修正案.md | Noto CJK が TTC のため reportlab で使用できない旨、PDF は IPA で対応 |
| docs/qrcode_design_plan/PDF文字化け問題_緊急調査分析_修正案.md | フォントパス・Docker と Render の関係 |
| docs/qrcode_design_plan/デプロイ確認結果_フォントインストール確認.md | フォントパス一覧・IPA opentype の存在 |
| docs/qrcode_design_plan/QRコードデザイン変更_完全調査分析_修正案_ステップ計画.md | 日本語フォント登録案（IPA 優先・TTC は登録しない方針） |
| backend/Dockerfile | 現行のフォントパッケージ（fonts-dejavu, fonts-noto-cjk, fonts-ipafont, fonts-ipafont-gothic） |
| backend/app/services/qr_code_service.py | 現状の DejaVuSans-Bold 使用箇所（PNG/PDF） |

---

## 5. まとめ

- **Noto の経歴**: PDF 日本語用に Noto CJK を検討したが、**TTC のため reportlab では使用できず**、IPA ゴシック（.ttf）で対応済み。**失敗事例 = reportlab に TTC を渡すこと。**
- **今回の希望**: QRコードの「YadOPERA」を **モダン・スッキリ** にするため、**Noto Sans（Latin）** を利用する。
- **準備内容**:  
  - Dockerfile に `fonts-noto-core` を追加。  
  - `qr_code_service.py` で「YadOPERA」用フォントを **NotoSans-Bold.ttf** に差し替え（パスは Docker 内で確認）。  
  - SVG は `font-family` を Noto Sans に変更。  
  - PDF 日本語は従来どおり IPA（.ttf）のみ使用し、Noto CJK（.ttc）は登録しない。
---

**Document Version**: 1.1  
**Last Updated**: 2026年3月4日  
**Status**: 準備完了。A・B実装済み。ローカル／ステージングでのブラウザテスト・デプロイは手順書に従って実施すること。
