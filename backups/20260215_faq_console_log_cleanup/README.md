# バックアップ: FAQ の console.log 整理

**日付**: 2026年2月15日

## 変更内容

- **FaqManagement.vue**: デバッグ用の `console.log` を削除（fetchFaqs / onMounted / scroll / 削除・提案・無視の各ハンドラ）。`console.error`・`console.warn` は残す。
- **FaqList.vue**: `props.faqs` の watch 内の `console.log` と、`getFaqsByCategory` 内の `console.log` を削除。watch はログ専用のため watch ごと削除。
- **Dashboard.vue**: FAQ 管理へ遷移時の `console.log` 1 行を削除。

## 復元方法

```bash
cp backups/20260215_faq_console_log_cleanup/FaqManagement.vue frontend/src/views/admin/
cp backups/20260215_faq_console_log_cleanup/FaqList.vue frontend/src/components/admin/
cp backups/20260215_faq_console_log_cleanup/Dashboard.vue frontend/src/views/admin/
```
