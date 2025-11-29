# Render.com環境変数設定 修正

**問題**: `OPENAI_API_KEY`の値が「既存のOpenAI APIキー」という文字列のままになっている

---

## 修正が必要な環境変数

### OPENAI_API_KEY

**現在の値（誤り）**: `既存のOpenAI APIキー`

**正しい値**: 実際のOpenAI APIキー（`sk-`で始まる文字列）

---

## 修正手順

1. Render.comダッシュボードで、`OPENAI_API_KEY`環境変数を編集
2. 値の部分を実際のOpenAI APIキーに置き換える
3. 保存

---

## OpenAI APIキーの確認方法

OpenAI APIキーは以下のいずれかで確認できます:

1. **OpenAI Platform**: https://platform.openai.com/api-keys
2. **ローカルの`.env`ファイル**: `backend/.env`ファイルに`OPENAI_API_KEY`が記載されている可能性があります
3. **以前の設定**: 以前に設定した場所から確認

---

## 注意事項

- OpenAI APIキーは`sk-`で始まる文字列です
- キーは機密情報なので、他人に共有しないでください
- キーを忘れた場合は、OpenAI Platformで新しいキーを生成できます

---

## 次のステップ

`OPENAI_API_KEY`を修正したら:
1. デプロイが自動的に再実行されます
2. 動作確認に進みます

