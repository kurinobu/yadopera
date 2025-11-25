FROM node:18-alpine

WORKDIR /app

# 依存関係ファイルのコピーとインストール
COPY package.json package-lock.json* ./
RUN npm install

# アプリケーションコードのコピー
COPY . .

# ポート公開
EXPOSE 5173

# デフォルトコマンド（docker-compose.ymlで上書き可能）
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

