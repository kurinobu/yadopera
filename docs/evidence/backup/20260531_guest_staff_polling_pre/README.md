# バックアップ — ゲスト staff 返信ポーリング実装前

**作成日**: 2026-05-31  
**Git ブランチ**: `backup/20260531-guest-staff-polling-pre`（`544b6f7` 時点）  
**作業ブランチ**: `feature/guest-staff-reply-polling`

## 含まれるファイル（変更前のコピー）

- `Chat.vue`
- `ChatMessage.vue`
- `useChat.ts`

## 復元方法

```bash
cp docs/evidence/backup/20260531_guest_staff_polling_pre/Chat.vue frontend/src/views/guest/Chat.vue
cp docs/evidence/backup/20260531_guest_staff_polling_pre/ChatMessage.vue frontend/src/components/guest/ChatMessage.vue
cp docs/evidence/backup/20260531_guest_staff_polling_pre/useChat.ts frontend/src/composables/useChat.ts
```

または `git checkout backup/20260531-guest-staff-polling-pre -- <paths>`
