# バックアップ: INP・CLS の改善（報告書 5.4）

**日付**: 2026年2月15日  
**対応**: 報告書 5.4「INP・CLS の改善」

## 変更内容

- **CLS**: ローディング表示から実データ表示への切り替えでレイアウトが変わらないよう、ダッシュボード・FAQ管理のコンテンツエリアに **min-height** を指定し、スケルトン表示は行わず同じ枠の高さを確保する。
- **INP**: ボタンクリックで即座に **ローディング状態（disabled）** を出し、重い処理は **setTimeout(0)** で次のタスクに回す。FaqList では **getFaqsByCategory の重複呼び出し** をやめ、**算出プロパティ（faqsByCategory）** でカテゴリ別一覧を1回だけ計算する。

## 対象ファイル

- `frontend/src/views/admin/Dashboard.vue`
- `frontend/src/views/admin/FaqManagement.vue`
- `frontend/src/components/admin/FaqList.vue`

## 復元方法

```bash
cp backups/20260215_inp_cls_improvement/Dashboard.vue frontend/src/views/admin/
cp backups/20260215_inp_cls_improvement/FaqManagement.vue frontend/src/views/admin/
cp backups/20260215_inp_cls_improvement/FaqList.vue frontend/src/components/admin/
```
