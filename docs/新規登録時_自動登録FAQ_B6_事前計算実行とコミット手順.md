# B6 手順：事前計算の実行と JSON のコミット

**目的**: Phase B Step B6。FAQ プリセット用の埋め込みを事前計算し、`faq_presets_embeddings.json` を生成してリポジトリにコミットする。

**参照**: `docs/新規登録時_自動登録FAQ_埋め込み事前計算_実装計画.md` §9 Phase B（B6）

---

## 実行場所

**自分のPCのターミナル**で行う。ここでしか使わない。サーバーや他のシェルではない。

---

## OPENAI_API_KEY

`backend/.env` に `OPENAI_API_KEY=sk-...` の行があれば、Docker が読み込む。それだけ。

---

## 手順（コピペだけでよい）

### 1. 事前計算を実行する

ターミナルで、以下を**この順に1行ずつコピーして貼り付け、Enter**する。

```bash
cd /Users/kurinobu/projects/yadopera
```

```bash
docker-compose run --rm backend python scripts/generate_faq_presets_embeddings.py
```

終了時に `Written 210 embeddings to ...` と出れば成功。`backend/app/data/faq_presets_embeddings.json` ができる。

---

### 2. 生成ファイルをコミットする

同じターミナルで、以下を**この順に1行ずつコピーして貼り付け、Enter**する。

```bash
git add backend/app/data/faq_presets_embeddings.json
```

```bash
git commit -m "chore: add precomputed FAQ preset embeddings (Phase B6)"
```

プッシュする場合は:

```bash
git push origin develop
```

---

## 次のステップ（B7）

B6 が終わったら B7（auth_service の変更）に進む。
