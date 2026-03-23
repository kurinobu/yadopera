# ローカルブラウザテスト 即実行用（URL・コピペ用質問）

**更新**: 2026年2月14日  
Docker 起動後、このファイルのURLを開き、下記の質問をコピペしてチャットで送信してください。

---

## 1. テスト用URL

| 用途 | URL |
|------|-----|
| **ゲスト・5言語（Premium）** | **http://localhost:5173/f/test-hotel-premium-d4bdfcae** |
| ゲスト・4言語（Standard） | http://localhost:5173/f/test-hotel-standard-17d4c0ca |
| ゲスト・3言語（Small） | http://localhost:5173/f/phase-d-small-test-d2feae4c |
| フロントトップ | http://localhost:5173 |
| バックエンドヘルス | http://localhost:8000/api/v1/health |

**まず開くURL**: **http://localhost:5173/f/test-hotel-premium-d4bdfcae**

---

## 2. コピペ用 質問一覧（言語別）

### 日本語（ja）

```
チェックインは何時からですか？
```

```
WiFiのパスワードを教えてください
```

```
夜は何時から静かにする必要がありますか？
```

---

### English（en）

```
What time is check-in?
```

```
What is the WiFi password?
```

```
When do we need to be quiet at night?
```

---

### 繁體中文（zh-TW）

```
晚上有安靜規定嗎？
```

```
淋浴隨時可以使用嗎？
```

```
最近車站怎麼走？
```

---

### Français（fr）

```
Y a-t-il des règles de calme la nuit ?
```

```
Puis-je utiliser la douche à tout moment ?
```

```
Comment aller à la gare la plus proche ?
```

---

### 한국어（ko）

```
밤에 정숙 규칙이 있나요?
```

```
샤워는 언제든 사용할 수 있나요?
```

```
가장 가까운 역까지 어떻게 가나요?
```

---

## 3. 「回答言語 = 選択言語」強制の確認用（コピペ用）

**手順**: 言語選択で **韓国語（한국어）** を選ぶ → チャットで **中国語の質問** を送信 → 回答が **韓国語** で返ることを確認。

```
WiFi密码是什么？
```

**手順**: 言語選択で **日本語** を選ぶ → チャットで **英語の質問** を送信 → 回答が **日本語** で返ることを確認。

```
What is the WiFi password?
```

---

## 4. 起動コマンド（参照）

```bash
cd /Users/kurinobu/projects/yadopera
docker-compose up -d --build
```

状態確認: `docker-compose ps`  
バックエンド再起動: `docker-compose restart backend`
