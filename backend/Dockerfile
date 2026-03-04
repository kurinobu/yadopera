FROM python:3.11-slim

WORKDIR /app

# システム依存関係のインストール（IPAゴシックは apt で /usr/share/ に入る）
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    fonts-dejavu \
    fonts-noto-cjk \
    fonts-ipafont \
    fonts-ipafont-gothic \
    && rm -rf /var/lib/apt/lists/*

# Python依存関係のコピーとインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# キャッシュ無効化: RENDER_GIT_COMMIT は Render がビルド時に注入。未設定時は CACHEBUST を利用
ARG RENDER_GIT_COMMIT=
ARG CACHEBUST=1
RUN echo "${RENDER_GIT_COMMIT:-$CACHEBUST}" > /tmp/cachebust

# PDF用日本語フォントを単体でコピー（必ず実行され /app/fonts/ に配置）
COPY fonts/ /app/fonts/
RUN test -f /app/fonts/ipagp.ttf || (echo "FATAL: ipagp.ttf missing." && exit 1)

# アプリケーションコードのコピー
COPY . .

# apt で入れた IPA を /app/fonts/ に必ず配置（COPY キャッシュに依存しない）
RUN mkdir -p /app/fonts && cp /usr/share/fonts/opentype/ipafont-gothic/ipagp.ttf /app/fonts/ && test -f /app/fonts/ipagp.ttf || (echo "FATAL: ipagp.ttf from apt missing." && exit 1)

# ポート公開
EXPOSE 8000

# デフォルトコマンド（docker-compose.ymlで上書き可能）
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
