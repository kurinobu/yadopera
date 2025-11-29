# pgvector拡張有効化 現在の進捗

**日時**: 2025年11月28日

---

## 完了したステップ

- ✅ プロジェクトルートディレクトリに移動
- ✅ Railway CLIでログイン完了
- ✅ プロジェクトをリンク完了（yadopera-postgres-staging）
- ✅ PostgreSQLサービスに接続完了（psql起動）

---

## 次のステップ

### ステップ5: pgvector拡張を有効化

psqlのプロンプトで、以下のSQLを実行してください:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

**実行方法**:
- SQLをコピー＆ペースト
- Enterキーを押す

---

## 注意事項

- SQLコマンドの末尾にセミコロン（;）が必要です
- 成功すると「CREATE EXTENSION」というメッセージが表示されます
