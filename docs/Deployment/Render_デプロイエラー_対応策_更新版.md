# Render.comデプロイエラー 対応策（更新版）

**エラー内容**: `pydantic-core==2.14.6`のビルド中にRustツールチェーンの問題が発生

**原因**: 
- Render.comがPython 3.13.4を使用している
- `pydantic-core==2.14.6`がRustツールチェーンを必要とするが、Render.comのビルド環境でビルドに失敗

**確認済み**: Render.comでPython 3.11は使用可能

---

## 対応策

### 対応策1: 環境変数でPython 3.11を指定（推奨）

**理由**:
- Render.comのドキュメントで推奨されている方法
- 設定が簡単で確実
- Dockerfileと一致している（Python 3.11）

**手順**:
1. Render.comダッシュボードでWeb Serviceを選択
2. 「Environment」タブを開く
3. 新しい環境変数を追加:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.11.8`（または`3.11.9`）
4. 保存
5. 再デプロイ（自動的に開始される）

---

### 対応策2: `.python-version`ファイルで指定

**手順**:
1. `backend/.python-version`ファイルを作成
2. 内容: `3.11.8`（または`3.11.9`）
3. 変更をコミット・プッシュ
4. Render.comで自動的に再デプロイが開始される

**ファイル**: `backend/.python-version`
```
3.11.8
```

---

### 対応策3: `runtime.txt`ファイルで指定

**手順**:
1. `backend/runtime.txt`ファイルを作成
2. 内容: `python-3.11.9`（`python-`プレフィックスが必要）
3. 変更をコミット・プッシュ
4. Render.comで自動的に再デプロイが開始される

**ファイル**: `backend/runtime.txt`
```
python-3.11.9
```

---

## 推奨対応

**対応策1（環境変数で指定）**を推奨します。

**理由**:
- 最も確実な方法
- Render.comのドキュメントで推奨されている
- 設定が簡単で、すぐに反映される
- ファイルを追加する必要がない

---

## 実装手順（対応策1を選択した場合）

1. Render.comダッシュボードでWeb Service（`yadopera-backend-staging`）を選択
2. 「Environment」タブを開く
3. 「Add Environment Variable」をクリック
4. 環境変数を追加:
   - **Key**: `PYTHON_VERSION`
   - **Value**: `3.11.8`
5. 保存
6. 再デプロイ（自動的に開始される）

---

## 確認事項

- Python 3.11.8はRender.comで利用可能（確認済み）
- 環境変数を追加すると、自動的に再デプロイが開始される
- デプロイ完了後、エラーが解消されているか確認

---

**次のステップ**: 対応策1（環境変数）でPython 3.11を指定して、デプロイを試してください。

