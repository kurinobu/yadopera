# Render.comデプロイエラー 対応策

**エラー内容**: `pydantic-core==2.14.6`のビルド中にRustツールチェーンの問題が発生

**エラーメッセージ**: 
```
error: failed to create directory `/usr/local/cargo/registry/cache/index.crates.io-1949cf8c6b5b557f`
Caused by: Read-only file system (os error 30)
```

**原因**: 
- Render.comがPython 3.13.4を使用している
- `pydantic-core==2.14.6`がRustツールチェーンを必要とするが、Render.comのビルド環境でビルドに失敗

---

## 対応策

### 対応策1: Pythonバージョンを3.11に指定（推奨）

**理由**:
- DockerfileではPython 3.11を使用している
- Python 3.11では`pydantic-core`のビルド済みwheelが利用可能
- Python 3.13では一部のパッケージがビルドを必要とする

**手順**:
1. `backend/runtime.txt`ファイルを作成
2. 内容: `python-3.11.9`
3. 変更をコミット・プッシュ
4. Render.comで自動的に再デプロイが開始される

**ファイル**: `backend/runtime.txt`
```
python-3.11.9
```

---

### 対応策2: pydanticのバージョンを更新

**理由**:
- 新しいバージョンのpydanticでは、Python 3.13用のビルド済みwheelが利用可能な可能性がある

**手順**:
1. `backend/requirements.txt`の`pydantic==2.5.3`を最新版に更新
2. 互換性を確認
3. 変更をコミット・プッシュ

**注意**: バージョン更新により、他の依存関係との互換性問題が発生する可能性がある

---

### 対応策3: Render.comの設定でPythonバージョンを指定

**手順**:
1. Render.comダッシュボードでWeb Serviceを選択
2. 「Settings」タブを開く
3. 「Python Version」を3.11に設定（設定項目がある場合）

**注意**: Render.comのUIによっては、この設定項目がない可能性がある

---

## 推奨対応

**対応策1（Pythonバージョンを3.11に指定）**を推奨します。

**理由**:
- 最も確実な方法
- Dockerfileと一致している
- 既存の依存関係との互換性が保証されている

---

## 実装手順（対応策1を選択した場合）

1. `backend/runtime.txt`ファイルを作成
   - 内容: `python-3.11.9`

2. 変更をコミット・プッシュ
   ```bash
   git add backend/runtime.txt
   git commit -m "Fix: Specify Python 3.11 for Render.com deployment"
   git push origin develop
   ```

3. Render.comで再デプロイ
   - 変更がプッシュされると、Render.comで自動的に再デプロイが開始されます
   - または、Render.comダッシュボードで「Manual Deploy」をクリック

---

## 確認事項

- `runtime.txt`は`backend/`ディレクトリに配置する必要がある
- Render.comは`runtime.txt`を読み取ってPythonバージョンを決定する
- Python 3.11.9はRender.comで利用可能なバージョンであることを確認

---

**次のステップ**: 対応策を選択して、実装してください。

