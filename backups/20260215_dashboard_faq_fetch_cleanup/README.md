# バックアップ: ダッシュボード表示時の FAQ 取得の整理

**日付**: 2026年2月15日  
**対応**: 報告書 5.3.3「ダッシュボード表示時の FAQ 取得の整理」

## 変更内容

- **対象**: `frontend/src/layouts/AdminLayout.vue`
- **修正**: レイアウトの `onMounted` で行っていた「初回 FAQ データ読み込み」を削除する。
- **理由**: ダッシュボード表示時に `faqs?language=ja` が呼ばれ、不要な待ち時間・リクエストが発生していた。FAQ はヘルプモーダルを開いたとき（`HelpModal.vue` の watch）にのみ取得するようにし、ダッシュボード表示時には FAQ を取得しない。

## 復元方法

```bash
cp backups/20260215_dashboard_faq_fetch_cleanup/AdminLayout.vue frontend/src/layouts/AdminLayout.vue
```
