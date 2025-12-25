# Phase 1: フロントエンドエラー 分析評価・修正案

**作成日**: 2025年12月3日  
**実施者**: Auto (AI Assistant)  
**対象**: フロントエンドのViteインポートエラー  
**状態**: ✅ **分析評価完了、根本原因特定完了**

---

## 1. エラーの説明と評価

### 1.1 エラー内容

**Viteインポートエラー**:
```
[plugin:vite:import-analysis] Failed to resolve import "@vueuse/integrations/useCookies" from "src/composables/useSession.ts". Does the file exist?
```

**HTTP 500エラー**:
```
GET http://localhost:5173/src/composables/useSession.ts net::ERR_ABORTED 500 (Internal Server Error)
```

**Vue Routerエラー**:
```
TypeError: Failed to fetch dynamically imported module: http://localhost:5173/src/views/guest/Chat.vue
```

### 1.2 エラーの評価

**根本原因**: Dockerコンテナ内で`@vueuse/integrations`パッケージがインストールされていない

**詳細**:
1. `package.json`には`@vueuse/integrations`が`^14.1.0`で定義されている
2. ホストマシンでは`node_modules/@vueuse/integrations`が存在する
3. しかし、Dockerコンテナ内では`node_modules/@vueuse/integrations`が存在しない
4. そのため、Viteがモジュールを解決できず、エラーが発生している

---

## 2. 根本原因の分析

### 2.1 Docker Composeのボリュームマウント設定

**docker-compose.ymlの設定**:
```yaml
frontend:
  volumes:
    - ./frontend:/app
    - /app/node_modules
```

**問題点**:
- `./frontend:/app`でホストの`frontend`ディレクトリをコンテナの`/app`にマウントしている
- `/app/node_modules`は匿名ボリュームで、ホストの`node_modules`を上書きしている
- しかし、Dockerコンテナ内で`npm install`が実行されていない、または実行されてもボリュームマウントで上書きされている可能性がある

### 2.2 Dockerfileの確認

**Dockerfile**:
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install
COPY . .
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
```

**問題点**:
- `npm install`は実行されているが、`COPY . .`の後に実行されていない
- ボリュームマウントで`./frontend:/app`がマウントされているため、Dockerfileでインストールした`node_modules`が上書きされている可能性がある

### 2.3 確認結果

**Dockerコンテナ内の確認**:
```bash
docker-compose exec frontend ls -la node_modules/@vueuse/integrations
# 結果: No such file or directory
```

**結論**:
- Dockerコンテナ内で`@vueuse/integrations`がインストールされていない
- ボリュームマウントでホストの`node_modules`がマウントされているが、ホストの`node_modules`が不完全である可能性がある
- または、Dockerコンテナ内で`npm install`が実行されていない

---

## 3. 修正案

### 3.1 修正方法1: Dockerコンテナ内でnpm installを実行（推奨）

**目的**: Dockerコンテナ内で`@vueuse/integrations`をインストールする

**実施内容**:
1. Dockerコンテナ内で`npm install`を実行:
   ```bash
   docker-compose exec frontend npm install
   ```
2. フロントエンドコンテナを再起動:
   ```bash
   docker-compose restart frontend
   ```
3. 動作確認:
   - ブラウザでページをリロード
   - エラーが解消されているか確認

**メリット**:
- 簡単で迅速
- 既存の設定を変更する必要がない

**デメリット**:
- コンテナを再起動すると、`node_modules`が失われる可能性がある（ボリュームマウントの設定による）

### 3.2 修正方法2: ホストマシンでnpm installを実行

**目的**: ホストマシンの`node_modules`を完全にする

**実施内容**:
1. ホストマシンで`npm install`を実行:
   ```bash
   cd frontend
   npm install
   ```
2. フロントエンドコンテナを再起動:
   ```bash
   docker-compose restart frontend
   ```
3. 動作確認:
   - ブラウザでページをリロード
   - エラーが解消されているか確認

**メリット**:
- ホストマシンの`node_modules`が完全になる
- ボリュームマウントでコンテナに反映される

**デメリット**:
- ホストマシンとコンテナのNode.jsバージョンが異なる場合、問題が発生する可能性がある

### 3.3 修正方法3: docker-compose.ymlのボリュームマウント設定を修正

**目的**: ボリュームマウントの設定を最適化する

**実施内容**:
1. `docker-compose.yml`を修正:
   ```yaml
   frontend:
     volumes:
       - ./frontend:/app
       - /app/node_modules  # 匿名ボリュームでnode_modulesを保護
     command: sh -c "npm install && npm run dev -- --host 0.0.0.0"
   ```
2. フロントエンドコンテナを再起動:
   ```bash
   docker-compose down frontend
   docker-compose up -d frontend
   ```
3. 動作確認:
   - ブラウザでページをリロード
   - エラーが解消されているか確認

**メリット**:
- コンテナ起動時に自動的に`npm install`が実行される
- ボリュームマウントで`node_modules`が保護される

**デメリット**:
- 起動時間が長くなる
- 設定変更が必要

### 3.4 修正方法4: Dockerfileを修正してnode_modulesを保護

**目的**: Dockerfileで`node_modules`を正しくインストールし、ボリュームマウントで保護する

**実施内容**:
1. `Dockerfile`を修正:
   ```dockerfile
   FROM node:18-alpine
   WORKDIR /app
   COPY package.json package-lock.json* ./
   RUN npm install
   COPY . .
   EXPOSE 5173
   CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
   ```
2. `docker-compose.yml`を確認（既に`/app/node_modules`が匿名ボリュームとして設定されている）
3. フロントエンドコンテナを再ビルド:
   ```bash
   docker-compose build frontend
   docker-compose up -d frontend
   ```
4. 動作確認:
   - ブラウザでページをリロード
   - エラーが解消されているか確認

**メリット**:
- Dockerイメージに`node_modules`が含まれる
- ボリュームマウントで保護される

**デメリット**:
- イメージサイズが大きくなる
- 再ビルドが必要

---

## 4. 推奨される修正方法

### 4.1 最優先: 修正方法1（Dockerコンテナ内でnpm installを実行）

**理由**:
1. 最も簡単で迅速
2. 既存の設定を変更する必要がない
3. 即座に問題を解決できる

**実施手順**:
1. Dockerコンテナ内で`npm install`を実行
2. フロントエンドコンテナを再起動
3. 動作確認

### 4.2 根本解決: 修正方法3（docker-compose.ymlの修正）

**理由**:
1. コンテナ起動時に自動的に`npm install`が実行される
2. ボリュームマウントで`node_modules`が保護される
3. 長期的な解決策

**実施手順**:
1. `docker-compose.yml`を修正
2. フロントエンドコンテナを再起動
3. 動作確認

---

## 5. 次のステップ

### 5.1 即座の修正（修正方法1）

**実施内容**:
1. Dockerコンテナ内で`npm install`を実行
2. フロントエンドコンテナを再起動
3. 動作確認

### 5.2 根本解決（修正方法3）

**実施内容**:
1. `docker-compose.yml`を修正
2. フロントエンドコンテナを再起動
3. 動作確認

---

## 6. まとめ

### 6.1 根本原因

**問題**: Dockerコンテナ内で`@vueuse/integrations`パッケージがインストールされていない

**詳細**:
- `package.json`には`@vueuse/integrations`が定義されている
- しかし、Dockerコンテナ内では`node_modules/@vueuse/integrations`が存在しない
- ボリュームマウントの設定により、ホストの`node_modules`がマウントされているが、不完全である可能性がある

### 6.2 修正方法

**推奨**: 修正方法1（Dockerコンテナ内でnpm installを実行）

**実施手順**:
1. `docker-compose exec frontend npm install`
2. `docker-compose restart frontend`
3. 動作確認

### 6.3 重要なポイント

1. **即座の修正**: Dockerコンテナ内で`npm install`を実行すれば、問題は解決する
2. **根本解決**: `docker-compose.yml`を修正して、コンテナ起動時に自動的に`npm install`が実行されるようにする
3. **ボリュームマウント**: `/app/node_modules`を匿名ボリュームとして設定することで、ホストの`node_modules`が上書きされないようにする

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-03  
**Status**: ✅ **分析評価完了、根本原因特定完了**


