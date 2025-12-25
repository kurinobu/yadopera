"""
FAQをインテントベースの構造に移行するスクリプト

【目的】
既存のFAQデータを新しい構造（インテントベース）に移行する

【処理内容】
1. 既存FAQデータの分析: 同じfacility_id、同じcategory、同じquestion（意味的に同じ）のFAQをグループ化
2. 各グループからintent_keyを生成（例: basic_checkout_time）
3. データ移行: 各グループから1つのFAQレコードを作成（intent_keyを設定）、各グループの各言語のFAQをfaq_translationsテーブルに移動

【注意事項】
- このスクリプトはステップ2のマイグレーション実行後に実行する必要があります
- ステップ2のマイグレーションで既に基本的なデータ移行は完了していますが、intent_keyは一時的に'legacy_' + idが設定されています
- このスクリプトで適切なintent_keyを生成し、意味的に同じFAQを統合します
"""

import asyncio
import sys
import os
import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, text, update, delete
from app.core.config import settings

# すべてのモデルをインポート（リレーションシップ解決のため）
from app.models.faq import FAQ
from app.models.facility import Facility

logger = None


def normalize_question(question: str) -> str:
    """
    質問文を正規化してintent_keyを生成するためのキーを作成
    
    Args:
        question: 質問文
    
    Returns:
        正規化された質問文（小文字、記号除去、空白正規化）
    """
    if not question:
        return ""
    
    # 小文字に変換
    normalized = question.lower()
    
    # 記号を除去（ハイフン、アンダースコアは保持）
    normalized = re.sub(r'[^\w\s\-_]', '', normalized)
    
    # 複数の空白を1つに
    normalized = re.sub(r'\s+', '_', normalized)
    
    # 前後の空白を削除
    normalized = normalized.strip('_')
    
    # 長さを制限（100文字以内）
    if len(normalized) > 100:
        normalized = normalized[:100]
    
    return normalized


def generate_intent_key(category: str, question: str) -> str:
    """
    インテントキーを生成
    
    Args:
        category: カテゴリ（basic, facilities, location, trouble）
        question: 質問文
    
    Returns:
        インテントキー（例: basic_checkout_time）
    """
    normalized_question = normalize_question(question)
    
    # カテゴリと正規化された質問文を結合
    intent_key = f"{category}_{normalized_question}"
    
    # 長さを制限（100文字以内）
    if len(intent_key) > 100:
        intent_key = intent_key[:100]
    
    return intent_key


async def analyze_existing_faqs(db: AsyncSession) -> Dict[Tuple[int, str, str], List[Dict]]:
    """
    既存のFAQデータを分析してグループ化
    
    注意: ステップ2のマイグレーションで既にfaq_translationsテーブルにデータが移行されていますが、
    同じ意味のFAQが複数言語で存在する場合、別々のFAQレコードとして存在しています。
    このスクリプトで、同じ意味のFAQをグループ化して統合します。
    
    Args:
        db: データベースセッション
    
    Returns:
        グループ化されたFAQデータ（キー: (facility_id, category, normalized_question), 値: FAQ情報のリスト）
    """
    print("📊 既存FAQデータの分析を開始...")
    
    # faq_translationsテーブルから既存のFAQデータを取得
    # 注意: ステップ2のマイグレーションで既にfaq_translationsテーブルにデータが移行されている
    result = await db.execute(text("""
        SELECT 
            f.id as faq_id,
            f.facility_id,
            f.category,
            f.intent_key as current_intent_key,
            f.priority,
            f.is_active,
            f.created_by,
            f.created_at,
            ft.language,
            ft.question,
            ft.answer,
            ft.embedding IS NOT NULL as has_embedding
        FROM faqs f
        INNER JOIN faq_translations ft ON f.id = ft.faq_id
        ORDER BY f.facility_id, f.category, ft.language
    """))
    
    rows = result.fetchall()
    
    # グループ化: (facility_id, category, normalized_question) -> List[FAQ情報]
    # 注意: 同じ意味のFAQが複数言語で存在する場合、質問文が異なるため、
    # 正規化後の文字列も異なる可能性があります。
    # そのため、より柔軟なグループ化方法を検討する必要がありますが、
    # まずは質問文の正規化でグループ化します。
    groups: Dict[Tuple[int, str, str], List[Dict]] = defaultdict(list)
    
    for row in rows:
        facility_id = row.facility_id
        category = row.category
        question = row.question
        normalized_question = normalize_question(question)
        
        key = (facility_id, category, normalized_question)
        groups[key].append({
            'faq_id': row.faq_id,
            'current_intent_key': row.current_intent_key,
            'priority': row.priority,
            'is_active': row.is_active,
            'created_by': row.created_by,
            'created_at': row.created_at,
            'language': row.language,
            'question': question,
            'answer': row.answer,
            'has_embedding': row.has_embedding
        })
    
    print(f"✅ 分析完了: {len(rows)}件のFAQ翻訳を{len(groups)}グループに分類")
    
    # 複数のFAQが含まれるグループを表示（デバッグ用）
    multi_faq_groups = {k: v for k, v in groups.items() if len(v) > 1}
    if multi_faq_groups:
        print(f"  📊 複数FAQを含むグループ: {len(multi_faq_groups)}グループ")
        for (facility_id, category, normalized_question), faq_list in list(multi_faq_groups.items())[:5]:
            print(f"    - facility_id={facility_id}, category={category}, FAQ数={len(faq_list)}")
    
    return groups


async def migrate_faq_data(db: AsyncSession, groups: Dict[Tuple[int, str, str], List[Dict]]) -> None:
    """
    FAQデータを新しい構造に移行
    
    注意: 同じ意味のFAQが複数言語で存在する場合、別々のFAQレコードとして存在しています。
    この関数で、同じ意味のFAQを統合します。
    
    Args:
        db: データベースセッション
        groups: グループ化されたFAQデータ
    """
    print("🔄 FAQデータの移行を開始...")
    
    migrated_count = 0
    merged_count = 0
    error_count = 0
    
    for (facility_id, category, normalized_question), faq_list in groups.items():
        try:
            # 各グループから代表FAQを選択
            # 優先順位: 1. 優先度が高いもの、2. 作成日時が古いもの、3. IDが小さいもの
            representative = sorted(
                faq_list,
                key=lambda x: (-x.get('priority', 1), x.get('created_at'), x.get('faq_id'))
            )[0]
            representative_faq_id = representative['faq_id']
            
            # intent_keyを生成（代表FAQの質問文を使用）
            intent_key = generate_intent_key(category, representative['question'])
            
            # UNIQUE制約のチェック: 同じfacility_id、同じintent_keyのFAQが既に存在するか確認
            check_result = await db.execute(text("""
                SELECT id FROM faqs 
                WHERE facility_id = :facility_id 
                AND intent_key = :intent_key 
                AND id != :current_faq_id
            """), {
                'facility_id': facility_id,
                'intent_key': intent_key,
                'current_faq_id': representative_faq_id
            })
            
            existing_faq = check_result.fetchone()
            if existing_faq:
                # 既に同じintent_keyのFAQが存在する場合、そちらに統合
                existing_faq_id = existing_faq.id
                print(f"  ⚠️ 既存のintent_keyを検出: facility_id={facility_id}, intent_key={intent_key}, 既存FAQ_id={existing_faq_id}")
                
                # 代表FAQの翻訳を既存FAQに移動
                await db.execute(text("""
                    UPDATE faq_translations
                    SET faq_id = :existing_faq_id
                    WHERE faq_id = :representative_faq_id
                """), {
                    'existing_faq_id': existing_faq_id,
                    'representative_faq_id': representative_faq_id
                })
                
                # 代表FAQを削除
                await db.execute(
                    delete(FAQ).where(FAQ.id == representative_faq_id)
                )
                
                # 他のFAQも既存FAQに統合
                other_faq_ids = [f['faq_id'] for f in faq_list if f['faq_id'] != representative_faq_id]
                for other_faq_id in other_faq_ids:
                    await db.execute(text("""
                        UPDATE faq_translations
                        SET faq_id = :existing_faq_id
                        WHERE faq_id = :other_faq_id
                    """), {
                        'existing_faq_id': existing_faq_id,
                        'other_faq_id': other_faq_id
                    })
                    await db.execute(
                        delete(FAQ).where(FAQ.id == other_faq_id)
                    )
                
                merged_count += len(faq_list)
                print(f"  ✅ 既存FAQに統合: facility_id={facility_id}, intent_key={intent_key}, 統合数={len(faq_list)}")
            
            # グループ内のFAQが複数ある場合（同じ意味のFAQが複数言語で存在）
            elif len(faq_list) > 1:
                # 代表FAQのintent_keyを更新
                await db.execute(
                    update(FAQ)
                    .where(FAQ.id == representative_faq_id)
                    .values(intent_key=intent_key)
                )
                
                # 他のFAQを統合（代表FAQに統合）
                other_faq_ids = [f['faq_id'] for f in faq_list if f['faq_id'] != representative_faq_id]
                
                # 他のFAQの翻訳を代表FAQに移動
                for other_faq_id in other_faq_ids:
                    # faq_translationsテーブルのfaq_idを更新
                    # 注意: 同じ言語の翻訳が既に存在する場合はスキップ（UNIQUE制約違反を回避）
                    await db.execute(text("""
                        UPDATE faq_translations
                        SET faq_id = :representative_faq_id
                        WHERE faq_id = :other_faq_id
                        AND NOT EXISTS (
                            SELECT 1 FROM faq_translations ft2
                            WHERE ft2.faq_id = :representative_faq_id
                            AND ft2.language = faq_translations.language
                        )
                    """), {
                        'representative_faq_id': representative_faq_id,
                        'other_faq_id': other_faq_id
                    })
                    
                    # 移動できなかった翻訳（同じ言語が既に存在）を削除
                    await db.execute(text("""
                        DELETE FROM faq_translations
                        WHERE faq_id = :other_faq_id
                    """), {
                        'other_faq_id': other_faq_id
                    })
                    
                    # 他のFAQを削除
                    await db.execute(
                        delete(FAQ).where(FAQ.id == other_faq_id)
                    )
                
                merged_count += len(other_faq_ids)
                print(f"  ✅ 統合: facility_id={facility_id}, category={category}, intent_key={intent_key}, 統合数={len(other_faq_ids)}")
            else:
                # 単一のFAQの場合、intent_keyを更新
                await db.execute(
                    update(FAQ)
                    .where(FAQ.id == representative_faq_id)
                    .values(intent_key=intent_key)
                )
                print(f"  ✅ 更新: facility_id={facility_id}, category={category}, intent_key={intent_key}")
            
            migrated_count += 1
            
        except Exception as e:
            error_count += 1
            print(f"  ❌ エラー: facility_id={facility_id}, category={category}, error={str(e)}")
            import traceback
            traceback.print_exc()
            continue
    
    await db.commit()
    
    print(f"✅ 移行完了: {migrated_count}グループ移行、{merged_count}件統合、{error_count}件エラー")


async def verify_migration(db: AsyncSession) -> None:
    """
    移行結果を検証
    
    Args:
        db: データベースセッション
    """
    print("🔍 移行結果の検証を開始...")
    
    # FAQ数と翻訳数の確認
    result = await db.execute(text("""
        SELECT 
            COUNT(DISTINCT f.id) as faq_count,
            COUNT(ft.id) as translation_count,
            COUNT(DISTINCT f.facility_id) as facility_count
        FROM faqs f
        LEFT JOIN faq_translations ft ON f.id = ft.faq_id
    """))
    
    row = result.fetchone()
    faq_count = row.faq_count
    translation_count = row.translation_count
    facility_count = row.facility_count
    
    print(f"  📊 FAQ数: {faq_count}件")
    print(f"  📊 翻訳数: {translation_count}件")
    print(f"  📊 施設数: {facility_count}件")
    print(f"  📊 平均翻訳数: {translation_count / faq_count if faq_count > 0 else 0:.2f}件/FAQ")
    
    # intent_keyの確認
    result = await db.execute(text("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT intent_key) as unique_intent_keys,
            COUNT(*) FILTER (WHERE intent_key LIKE 'legacy_%') as legacy_count
        FROM faqs
    """))
    
    row = result.fetchone()
    total = row.total
    unique_intent_keys = row.unique_intent_keys
    legacy_count = row.legacy_count
    
    print(f"  📊 総FAQ数: {total}件")
    print(f"  📊 ユニークintent_key数: {unique_intent_keys}件")
    print(f"  📊 一時的intent_key数: {legacy_count}件")
    
    if legacy_count > 0:
        print(f"  ⚠️ 警告: {legacy_count}件のFAQが一時的なintent_keyのままです")
    else:
        print(f"  ✅ すべてのFAQが適切なintent_keyを持っています")


async def main():
    """
    メイン処理
    """
    print("=" * 80)
    print("FAQインテントベース構造への移行スクリプト")
    print("=" * 80)
    print()
    
    # データベース接続
    engine = create_async_engine(
        settings.database_url,
        echo=False,
        future=True
    )
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    
    async with async_session() as db:
        try:
            # Step 1: 既存FAQデータの分析
            groups = await analyze_existing_faqs(db)
            
            if not groups:
                print("⚠️ 移行対象のFAQデータがありません")
                return
            
            # Step 2: データ移行
            await migrate_faq_data(db, groups)
            
            # Step 3: 移行結果の検証
            await verify_migration(db)
            
            print()
            print("=" * 80)
            print("✅ 移行完了")
            print("=" * 80)
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {str(e)}")
            import traceback
            traceback.print_exc()
            await db.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

