FROM python:3.11-slim

WORKDIR /app

# システム依存関係のインストール（フォントは /app/fonts にコピーして確実に参照）
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    fonts-dejavu \
    fonts-noto-cjk \
    fonts-ipafont \
    fonts-ipafont-gothic \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /app/fonts \
    && cp /usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf /app/fonts/

# Python依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . .

# ポート公開
EXPOSE 8000

# デフォルトコマンド（docker-compose.ymlで上書き可能）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


