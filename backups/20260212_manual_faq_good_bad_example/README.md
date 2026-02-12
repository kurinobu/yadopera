# バックアップ: マニュアル 4.7 FAQ良い例・避けたい例追加

**日時**: 2026-02-12  
**対象**: `frontend/src/views/admin/Manual.vue`

## 変更内容（本番側で実施）
- 4.7「FAQ作成のベストプラクティス」の「2. 回答文の書き方」から「必要に応じて、追加情報への案内を含めてください（例: 「詳細はフロントでお尋ねください」）」を削除（エスカレーション削減のため）
- 「✅ 良い例と避けたい例（回答は具体的に）」ブロックを追加（洗濯機の避けたい例・良い例）

## 復元方法
```bash
cp backups/20260212_manual_faq_good_bad_example/Manual.vue frontend/src/views/admin/Manual.vue
```
