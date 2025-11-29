# Phase 1 Week 4 ステップ1: Render.comデプロイエラー（環境変数設定ミス）分析レポート

**作成日**: 2025年11月28日  
**対象**: Render.com環境変数`DATABASE_URL`設定後のエラー分析  
**目的**: エラーの原因を特定し、正しい設定方法を提示

---

## 1. エラー分析

### 1.1 エラーログ

**エラー内容**: `ValueError: invalid literal for int() with base 10: 'port'`

**エラー発生箇所**:
```
File "/opt/render/project/src/.venv/lib/python3.11/site-packages/sqlalchemy/engine/url.py", line 900, in _parse_url
    components["port"] = int(components["port"])
                         ^^^^^^^^^^^^^^^^^^^^^^^
ValueError: invalid literal for int() with base 10: 'port'
```

### 1.2 エラーの流れ

1. **パッケージのインストール**: ✅ 成功
2. **`alembic upgrade head`の実行**: ❌ 失敗
   - `alembic/env.py`の`get_url()`関数が`settings.database_url`を取得
   - その値が`postgresql://postgres:password@host:port/database`という文字列リテラル
   - SQLAlchemyがURLをパースしようとする
   - `port`という文字列を整数に変換しようとして失敗

---

## 2. 根本原因

### 2.1 問題の本質

**環境変数`DATABASE_URL`の値がプレースホルダー文字列のまま**

**設定された値（推測）**:
```
postgresql://postgres:password@host:port/database
```

**問題点**:
- `host`、`port`、`database`が実際の値ではなく、プレースホルダー文字列のまま
- SQLAlchemyがURLをパースする際、`port`を整数に変換しようとして失敗

### 2.2 正しい設定値

**Railway PostgreSQLの実際の接続情報を使用する必要がある**

**正しい形式**:
```
postgresql://postgres:実際のパスワード@実際のホスト:実際のポート/実際のデータベース名
```

**例**（Railway PostgreSQL接続情報より）:
```
postgresql://postgres:q2qvotspe3muf84hanuy5lw6eascqt82@yamanote.proxy.rlwy.net:15647/railway
```

---

## 3. 評価

### 3.1 エラーの性質

**評価**: ⚠️ **環境変数設定ミス**

**理由**:
- エラー自体は正常な動作（SQLAlchemyがURLをパースしようとしている）
- 問題は、環境変数の値が実際の接続情報ではなく、プレースホルダー文字列のままであること

### 3.2 前回のエラーとの比較

**前回のエラー**:
- `MissingGreenlet`エラー
- 原因: 同期エンジンで非同期URLを使用しようとしている

**今回のエラー**:
- `ValueError: invalid literal for int() with base 10: 'port'`
- 原因: 環境変数の値がプレースホルダー文字列のまま

**進捗**:
- ✅ 前回のエラー（`MissingGreenlet`）は解決された
- ✅ 環境変数を`postgresql://`形式に変更した方針は正しい
- ❌ 環境変数の値が実際の接続情報に置き換えられていない

### 3.3 根本解決策の評価

**解決策1（環境変数を`postgresql://`形式に設定）の評価**:
- ✅ **方針は正しい**: 環境変数を`postgresql://`形式に変更する方針は正しい
- ✅ **前回のエラーは解決**: `MissingGreenlet`エラーは発生しなくなった
- ⚠️ **実装ミス**: 環境変数の値が実際の接続情報に置き換えられていない

**結論**: 根本解決策の方向性は正しいが、実装時に環境変数の値を実際の接続情報に置き換える必要がある

---

## 4. 正しい設定方法

### 4.1 Railway PostgreSQL接続情報の取得

**Railwayダッシュボードから取得**:
1. Railwayダッシュボードにログイン
2. PostgreSQLサービスを選択
3. 「**Variables**」タブを開く
4. `DATABASE_PUBLIC_URL`の値を確認

**例**:
```
postgresql://postgres:q2qvotspe3muf84hanuy5lw6eascqt82@yamanote.proxy.rlwy.net:15647/railway
```

### 4.2 Render.com環境変数の設定

**手順**:
1. Render.comダッシュボードでWeb Service（`yadopera-backend-staging`）を選択
2. 「**Environment**」タブを開く
3. `DATABASE_URL`環境変数を編集
4. 値をRailway PostgreSQLの`DATABASE_PUBLIC_URL`の値に設定
   - **重要**: `postgresql://`形式のまま（`postgresql+asyncpg://`に変更しない）

**設定例**:
```
postgresql://postgres:q2qvotspe3muf84hanuy5lw6eascqt82@yamanote.proxy.rlwy.net:15647/railway
```

### 4.3 確認事項

**設定後の確認**:
- [ ] `DATABASE_URL`の値が実際の接続情報になっている
- [ ] `postgresql://`形式になっている（`postgresql+asyncpg://`ではない）
- [ ] ホスト、ポート、データベース名が実際の値になっている
- [ ] パスワードが実際の値になっている

---

## 5. 期待される結果

### 5.1 正しい設定後の動作

**期待される流れ**:
1. **パッケージのインストール**: ✅ 成功
2. **`alembic upgrade head`の実行**: ✅ 成功
   - `alembic/env.py`の`get_url()`関数が`settings.database_url`を取得
   - その値が実際の接続情報（例: `postgresql://postgres:password@host:15647/railway`）
   - SQLAlchemyがURLをパースする
   - 同期エンジン（`engine_from_config`）が正常に作成される
   - Alembicマイグレーションが正常に実行される
3. **ビルドの成功**: ✅ 成功
4. **Web Serviceの起動**: ✅ 成功

### 5.2 アプリケーション側の動作確認

**`app/database.py`の変換処理**:
```python
database_url = settings.database_url
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
```

**確認**:
- ✅ `postgresql://`形式のURLを`postgresql+asyncpg://`形式に変換する処理が実装されている
- ✅ 環境変数`DATABASE_URL`を`postgresql://`形式に設定しても、アプリケーションは正常に動作する

---

## 6. まとめ

### 6.1 エラーの原因

**根本原因**: 環境変数`DATABASE_URL`の値がプレースホルダー文字列（`postgresql://postgres:password@host:port/database`）のまま

**問題点**:
- `host`、`port`、`database`が実際の値ではなく、プレースホルダー文字列のまま
- SQLAlchemyがURLをパースする際、`port`を整数に変換しようとして失敗

### 6.2 解決方法

**正しい設定**:
1. Railway PostgreSQLの`DATABASE_PUBLIC_URL`の値を取得
2. Render.comの環境変数`DATABASE_URL`にその値を設定
3. **重要**: `postgresql://`形式のまま（`postgresql+asyncpg://`に変更しない）

**設定例**:
```
postgresql://postgres:q2qvotspe3muf84hanuy5lw6eascqt82@yamanote.proxy.rlwy.net:15647/railway
```

### 6.3 評価

**根本解決策の評価**:
- ✅ **方針は正しい**: 環境変数を`postgresql://`形式に変更する方針は正しい
- ✅ **前回のエラーは解決**: `MissingGreenlet`エラーは発生しなくなった
- ⚠️ **実装ミス**: 環境変数の値が実際の接続情報に置き換えられていない

**結論**: 根本解決策の方向性は正しいが、実装時に環境変数の値を実際の接続情報に置き換える必要がある

---

## 7. 次のステップ

### 7.1 即座の対応

1. **Railway PostgreSQL接続情報の取得**
   - Railwayダッシュボードから`DATABASE_PUBLIC_URL`の値を取得

2. **Render.com環境変数の設定**
   - `DATABASE_URL`環境変数の値を実際の接続情報に設定
   - `postgresql://`形式のまま（`postgresql+asyncpg://`に変更しない）

3. **再デプロイ**
   - Render.comで自動デプロイが実行される
   - デプロイが成功することを確認

### 7.2 確認事項

- [ ] `DATABASE_URL`の値が実際の接続情報になっている
- [ ] `postgresql://`形式になっている
- [ ] デプロイが成功する
- [ ] Alembicマイグレーションが正常に実行される
- [ ] アプリケーションが正常に動作する

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-11-28  
**Status**: 環境変数設定ミスの分析完了

