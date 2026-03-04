# QRコード「YadOPERA」縦位置・Notoフォント ブラウザテスト手順

**作成日**: 2026年3月4日  
**対象**: A実装（縦位置上下中央）・B実装（Notoフォント）のローカル／ステージング確認

---

## 前提

- **A実装**: QRコード中央の「YadOPERA」を余白内で上下中央に配置（PNG/PDF/SVG）
- **B実装**: 上記テキストのフォントを Noto Sans Bold に変更（モダン・スッキリ）

---

## 1. ローカルでA実装をブラウザテスト（手順 2）

1. **Docker でバックエンド・フロント・DB 起動**
   ```bash
   cd /Users/kurinobu/projects/yadopera
   docker-compose up -d
   ```
2. 管理画面にログイン: `http://localhost:5173`（またはフロントのポート）
3. **QRコード生成** メニューを開く
4. 設置場所を選び **プレビュー生成** を実行
5. **確認項目**
   - **PNG**: 「YadOPERA」がQRコード中央の白い余白の**縦方向の中央**に表示されている
   - **PDF**: 同上（QR部分を確認）
   - **SVG**: 同上
6. 問題なければ **A実装 ローカルテスト完了**

---

## 2. ステージングにデプロイ（手順 3）

- 通常のデプロイ手順（Push to develop または Render のデプロイ）でステージングに反映

---

## 3. ステージングでA実装をブラウザテスト（手順 4）

1. ステージングの管理画面にログイン
2. QRコード生成 → プレビュー生成（PNG/PDF/SVG）
3. **確認項目**: ローカルと同様に「YadOPERA」が中央余白の**上下中央**になっていること

---

## 4. ローカルでB実装をブラウザテスト（手順 6）

1. **バックエンドを再ビルド**（Dockerfile に `fonts-noto-core` 追加のため）
   ```bash
   docker-compose build backend
   docker-compose up -d
   ```
2. 管理画面で QRコード生成 → プレビュー生成
3. **確認項目**
   - 「YadOPERA」のフォントが **Noto Sans** 風（よりモダン・スッキリ）に見える
   - 縦位置は引き続き上下中央（Aのまま）
   - PNG/PDF/SVG いずれも期待どおり

---

## 5. ステージングでB実装をブラウザテスト（手順 8）

- ステージングデプロイ後、上記 4 と同様の項目をステージング環境で確認

---

## 6. 問題時のロールバック

- **A のみ戻す**: `backups/20260304_qr_stepA_vertical_center/qr_code_service.py` を `backend/app/services/` に上書き
- **B のみ戻す**: `backups/20260304_qr_stepB_noto_font/` の `qr_code_service.py` と `Dockerfile` を復元
