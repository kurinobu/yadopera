"""seed ads: 楽天トラベル（Phase 1）

Revision ID: 020
Revises: 019
Create Date: 2026-03-04

Freeプラン広告 Phase 1。表示テキスト: PR：次の旅行先の宿を探す（楽天トラベル）
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = '020'
down_revision = '019'
branch_labels = None
depends_on = None

# 実装方針で指定された楽天トラベルアフィリエイト
AFFILIATE_URL = (
    "https://hb.afl.rakuten.co.jp/hgc/15132e76.272ee056.15132e77.f62b93e1/"
    "?pc=https%3A%2F%2Ftravel.rakuten.co.jp%2F&link_type=text&ut=eyJwYWdlIjoidXJsIiwidHlwZSI6InRleHQiLCJjb2wiOjF9"
)
DISPLAY_TITLE = "PR：次の旅行先の宿を探す（楽天トラベル）"


def upgrade() -> None:
    conn = op.get_bind()
    conn.execute(
        text("""
        INSERT INTO ads (title, description, url, affiliate_url, priority, active, created_at)
        VALUES (:title, :description, :url, :affiliate_url, :priority, :active, now())
        """),
        {
            "title": DISPLAY_TITLE,
            "description": "楽天トラベルで宿を検索",
            "url": "https://travel.rakuten.co.jp/",
            "affiliate_url": AFFILIATE_URL,
            "priority": 1,
            "active": True,
        }
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(text("DELETE FROM ads WHERE title = :title"), {"title": DISPLAY_TITLE})
