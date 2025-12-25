# pgvector拡張エラー 対応方法

**エラー内容**: `extension "vector" is not available`

**原因**: RailwayのPostgreSQLサービスにpgvector拡張がインストールされていない

---

## 解決方法

### 方法1: PostgreSQLのバージョンと拡張を確認

まず、現在のPostgreSQLのバージョンと利用可能な拡張を確認:

```sql
-- PostgreSQLバージョン確認
SELECT version();

-- 利用可能な拡張一覧を確認
SELECT * FROM pg_available_extensions WHERE name LIKE '%vector%';
```

### 方法2: pgvectorがインストールされたPostgreSQLテンプレートを使用

RailwayのPostgreSQLサービスにpgvectorが含まれていない場合、以下の選択肢があります:

1. **新しいPostgreSQLサービスを作成**（pgvector付きテンプレートを使用）
   - Railwayダッシュボードで「New」→「Database」→「pgvector-pg17」または「pgvector-pg18」を選択
   - 既存のPostgreSQLサービスを削除して新しく作成
   - **注意**: 既存データが失われる可能性があります

2. **既存のPostgreSQLサービスを維持**（pgvectorなしで進める）
   - 後でRender.comのデプロイ時にpgvectorが必要になった場合に対応
   - または、別の方法でpgvectorをインストール

---

## 推奨対応

現在のPostgreSQLサービスにデータがない場合（ステージング環境なので新規作成）:
- **新しいPostgreSQLサービスを作成**（pgvector付きテンプレートを使用）を推奨

既存データがある場合:
- まず、PostgreSQLのバージョンと利用可能な拡張を確認

---

## 次のステップ

1. まず、PostgreSQLのバージョンを確認
2. 利用可能な拡張を確認
3. 必要に応じて、pgvector付きのPostgreSQLサービスを作成


