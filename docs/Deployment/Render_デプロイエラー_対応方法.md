# Render.comデプロイエラー 対応方法

**エラー内容**: `pydantic-core==2.14.6`のビルド中にRustツールチェーンの問題が発生

**原因**: 
- Render.comがPython 3.13.4を使用している
- `pydantic-core`がRustツールチェーンを必要とするが、Render.comのビルド環境でビルドに失敗

---

## 解決方法: Pythonバージョンを3.11に指定

### ステップ1: runtime.txtを作成

`backend/runtime.txt`ファイルを作成し、Python 3.11を指定:

```
python-3.11.9
```

### ステップ2: 変更をコミット・プッシュ

```bash
git add backend/runtime.txt
git commit -m "Fix: Specify Python 3.11 for Render.com deployment"
git push origin develop
```

### ステップ3: Render.comで再デプロイ

- 変更がプッシュされると、Render.comで自動的に再デプロイが開始されます
- または、Render.comダッシュボードで「Manual Deploy」をクリック

---

## 理由

- DockerfileではPython 3.11を使用している
- Python 3.11では`pydantic-core`のビルド済みwheelが利用可能
- Python 3.13では一部のパッケージがビルドを必要とする

---

## 次のステップ

1. `runtime.txt`を作成
2. 変更をコミット・プッシュ
3. デプロイの完了を待つ
4. 動作確認


