# pgvector Deployボタンについて

**質問**: pgvectorをDeployではだめなのですか？

---

## Deployボタンの動作

「Deploy」ボタンは、**新しいPostgreSQLサービス（pgvector付き）を作成**するためのものです。

### Deployボタンを使用した場合

1. 新しいPostgreSQLサービスが作成される
2. 既存のPostgreSQLサービスとは別のサービスになる
3. 既存のデータは引き継がれない
4. 新しい接続URLが発行される

### 既存のPostgreSQLサービスにpgvectorを追加する場合

既存のPostgreSQLサービス（`yadopera-postgres-staging`）にpgvector拡張を追加するには、**SQLで有効化**する必要があります。

---

## 推奨方法

### 既存のPostgreSQLサービスを使用する場合（推奨）

既にPostgreSQLサービスが作成されているので、SQLでpgvector拡張を有効化する方法を推奨します。

**理由**:
- 既存の接続情報をそのまま使用できる
- データを失うリスクがない
- 設定が簡単

### 新しいPostgreSQLサービスを作成する場合

もし既存のPostgreSQLサービスにデータがなく、新しく作成し直しても問題ない場合は、「Deploy」ボタンを使用することも可能です。

**注意事項**:
- 既存の接続URLが無効になる
- 新しい接続URLを取得する必要がある
- Render.comの環境変数を更新する必要がある

---

## 結論

**既存のPostgreSQLサービスを使用する場合**: SQLでpgvector拡張を有効化（推奨）

**新しいPostgreSQLサービスを作成する場合**: Deployボタンを使用（既存データがない場合のみ）

---

**推奨**: 既存のPostgreSQLサービスにSQLでpgvector拡張を追加する方法を推奨します。


