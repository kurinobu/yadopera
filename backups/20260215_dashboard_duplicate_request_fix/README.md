# バックアップ: ダッシュボード重複リクエスト防止 修正前（2026-02-15）

- **作成日時**: 2026年2月15日
- **目的**: ダッシュボードの重複リクエスト防止（調査分析報告書 5.3.1 節）を実施する前の状態を保存

## 含まれるファイル

| ファイル | 元のパス |
|----------|----------|
| `Dashboard.vue` | `frontend/src/views/admin/Dashboard.vue` |

## 復元方法

```bash
cp backups/20260215_dashboard_duplicate_request_fix/Dashboard.vue frontend/src/views/admin/Dashboard.vue
```

## 実施した修正の概要

- **進行中フラグの導入**: `isFetching` ref を追加。`fetchDashboardData()` の先頭で `isFetching.value` が true なら即 return。取得開始時に true、finally で false に設定。
- **効果**: onMounted / onActivated / onBeforeRouteUpdate が短時間に複数回呼ばれても、同時に 2 本以上の dashboard API が発行されず、キャンセルやタイムアウトの一因を削減。

参照: `docs/宿泊施設ダッシュボード・FAQ表示遅延_調査分析報告_20260214.md` 第5.3.1節
