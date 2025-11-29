# Phase 1 テストコード問題調査分析レポート

**作成日**: 2025年11月29日  
**対象**: テストコードの更新とテストフィクスチャの改善  
**目的**: テストコードと実装の不整合を完全に調査分析し、修正を実施

---

## 1. 調査結果サマリー

### 1.1 問題の分類

**調査対象**: 失敗・エラーが発生しているテストファイル

**問題の種類**:
1. **モックのパスエラー** - `test_confidence.py`（8テスト）
2. **モデルの属性エラー** - `test_vector_search.py`（1テスト）
3. **エラーレスポンス形式の不一致** - `test_auth.py`（1テスト）
4. **キーワード検出の不整合** - `test_safety_check.py`（1テスト）
5. **データベース接続エラー** - 複数のテストファイル（多数）

---

## 2. 詳細な問題分析

### 2.1 test_confidence.pyの問題

**問題**: モックのパスが間違っている

**現在のコード**:
```python
@patch('app.ai.confidence.search_similar_patterns')
@patch('app.ai.confidence.generate_embedding')
```

**実装の確認**:
- `search_similar_patterns` は `app.ai.vector_search` モジュールに存在
- `generate_embedding` は `app.ai.embeddings` モジュールに存在
- `app.ai.confidence` モジュールにはこれらの関数は存在しない

**修正方針**:
- パッチのパスを正しいモジュールに変更
- `@patch('app.ai.vector_search.search_similar_patterns')`
- `@patch('app.ai.embeddings.generate_embedding')`

**影響範囲**: 8テスト（すべての `test_confidence.py` のテスト）

---

### 2.2 test_vector_search.pyの問題

**問題**: `QuestionPattern` モデルに `is_active` 属性が存在しない

**現在のコード**:
```python
pattern = QuestionPattern(
    facility_id=test_facility.id,
    pattern_embedding=mock_embedding,
    total_count=10,
    resolved_count=8,
    is_active=True,  # ← この属性が存在しない
)
```

**実装の確認**:
- `QuestionPattern` モデルには `is_active` 属性が存在しない
- モデル定義: `id`, `facility_id`, `pattern_embedding`, `total_count`, `resolved_count`, `resolution_rate`, `last_asked_at`, `created_at`, `updated_at`

**修正方針**:
- `is_active=True` を削除

**影響範囲**: 1テスト（`test_search_similar_patterns_with_data`）

---

### 2.3 test_auth.pyの問題

**問題**: エラーレスポンス形式の不一致

**現在のコード**:
```python
assert "error" in data
assert data["error"]["code"] == "VALIDATION_ERROR"
```

**実装の確認**:
- FastAPIのバリデーションエラーは `"detail"` キーを使用
- 形式: `{"detail": [{"loc": [...], "msg": "...", "type": "..."}]}`

**修正方針**:
- `"error"` キーの代わりに `"detail"` キーを確認
- エラーレスポンス形式をFastAPIの標準形式に合わせる

**影響範囲**: 1テスト（`test_login_validation_error`）

---

### 2.4 test_safety_check.pyの問題

**問題**: `"I need to evacuate"` が検出されない

**現在のコード**:
```python
("I need to evacuate", True),
```

**実装の確認**:
- `SAFETY_KEYWORDS` には `'evacuation'` は含まれているが、`'evacuate'` は含まれていない
- `check_safety_category()` は部分一致で検出するため、`'evacuation'` が含まれていれば `'evacuate'` も検出されるはずだが、実際には検出されていない

**実装コード**:
```python
SAFETY_KEYWORDS = [
    'fire', 'earthquake', 'evacuation', 'escape', 'escape route',
    'emergency exit', 'tsunami', 'typhoon',
    '火災', '火事', '地震', '避難', '非常口', '津波', '台風'
]
```

**問題の原因**:
- `'evacuation'` は `'evacuate'` の部分文字列ではない（逆）
- `'evacuate'` は `'evacuation'` の部分文字列であるが、キーワードリストには `'evacuation'` しかない

**修正方針**:
- `SAFETY_KEYWORDS` に `'evacuate'` を追加
- または、テストケースを `'evacuation'` を含むものに変更

**影響範囲**: 1テスト（`test_safety_keyword_detection`）

---

### 2.5 データベース接続エラー

**問題**: 多くのテストでデータベース接続エラーが発生

**エラーメッセージ**:
```
ERROR    sqlalchemy.pool.impl.AsyncAdaptedQueuePool:base.py:381 Exception terminating connection
```

**原因**:
- テストフィクスチャがテーブルを作成する前にデータを挿入しようとしている
- ステージング環境では既にテーブルが存在するため、テーブル作成をスキップしているが、テストフィクスチャがデータを挿入する際にテーブルが存在しない

**修正方針**:
- テストフィクスチャの実行順序を調整
- テーブル作成の確認を追加
- データのクリーンアップを改善

**影響範囲**: 多数のテスト（主にデータベースを使用するテスト）

---

## 3. 修正計画

### 3.1 優先度の高い修正

#### 修正1: test_confidence.pyのモックパス修正

**優先度**: **最高**

**内容**:
- `@patch('app.ai.confidence.search_similar_patterns')` → `@patch('app.ai.vector_search.search_similar_patterns')`
- `@patch('app.ai.confidence.generate_embedding')` → `@patch('app.ai.embeddings.generate_embedding')`

**影響**: 8テスト

#### 修正2: test_vector_search.pyのモデル属性修正

**優先度**: **高**

**内容**:
- `QuestionPattern` のインスタンス作成時に `is_active=True` を削除

**影響**: 1テスト

#### 修正3: test_auth.pyのエラーレスポンス形式修正

**優先度**: **高**

**内容**:
- `"error"` キーの代わりに `"detail"` キーを確認
- FastAPIの標準エラーレスポンス形式に合わせる

**影響**: 1テスト

#### 修正4: test_safety_check.pyのキーワード検出修正

**優先度**: **中**

**内容**:
- `SAFETY_KEYWORDS` に `'evacuate'` を追加
- または、テストケースを修正

**影響**: 1テスト

### 3.2 優先度の低い修正

#### 修正5: テストフィクスチャの改善

**優先度**: **中**

**内容**:
- テストフィクスチャの実行順序を調整
- テーブル作成の確認を追加
- データのクリーンアップを改善

**影響**: 多数のテスト

---

## 4. 修正実施

### 4.1 修正ファイル一覧

1. `backend/tests/test_confidence.py` - モックパス修正
2. `backend/tests/test_vector_search.py` - モデル属性修正
3. `backend/tests/test_auth.py` - エラーレスポンス形式修正
4. `backend/app/ai/safety_check.py` - キーワード追加（またはテストケース修正）

---

## 5. 期待される結果

### 5.1 修正後のテスト結果

**期待される改善**:
- `test_confidence.py`: 8テスト → 0エラー（すべて成功）
- `test_vector_search.py`: 1テスト → 0エラー（成功）
- `test_auth.py`: 1テスト → 0エラー（成功）
- `test_safety_check.py`: 1テスト → 0エラー（成功）

**合計**: 11テストの修正

---

## 6. 次のステップ

### 6.1 修正実施

1. ✅ バックアップ完了
2. ⏳ 修正実施
3. ⏳ テスト再実行
4. ⏳ 結果確認

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-11-29  
**Status**: 調査分析完了、修正準備完了

