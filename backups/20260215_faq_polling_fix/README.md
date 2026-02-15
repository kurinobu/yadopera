# バックアップ: FAQポーリング根本修正前（2026-02-15）

- **作成日時**: 2026年2月15日
- **目的**: FAQ ポーリングの根本修正（調査分析報告書 5.2 節）を実施する前の状態を保存

## 含まれるファイル

| ファイル | 元のパス |
|----------|-----------|
| `faqs.py` | `backend/app/api/v1/admin/faqs.py` |
| `FaqManagement.vue` | `frontend/src/views/admin/FaqManagement.vue` |

## 復元方法

```bash
cp backups/20260215_faq_polling_fix/faqs.py backend/app/api/v1/admin/faqs.py
cp backups/20260215_faq_polling_fix/FaqManagement.vue frontend/src/views/admin/FaqManagement.vue
```

## 実施した修正の概要

1. **バックエンド**: `is_initializing` を「施設作成から 120 秒以内」かつ「actual_count < expected_count」のときのみ `True` に変更。単に FAQ が 20 件未満の施設では `False` を返すようにした。
2. **フロント**: ポーリング開始条件を「`isInitializing === true` のときのみ」に変更。終了条件を「`newIsInitializing === false`」に統一。冗長な console.log を削除。

参照: `docs/宿泊施設ダッシュボード・FAQ表示遅延_調査分析報告_20260214.md` 第5.2節
