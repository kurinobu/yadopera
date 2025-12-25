# Phase 0 ステップ10-4: Google Analytics設定 調査分析レポート

**作成日**: 2025年11月26日  
**目的**: ステップ10-4（Google Analytics設定）の準備状況調査と分析  
**ステータス**: 準備完了、DNS反映待ち

---

## 1. 現在の状況

### 1.1 完了済みステップ

| ステップ | ステータス | 完了日 | 備考 |
|---------|----------|--------|------|
| ステップ10-1: LP実装・改善 | ✅ 完了 | 2025-11-26 | PoC説明追加、カラーリング変更、Formspree実装 |
| ステップ10-2: Vercelデプロイ | ✅ 完了 | 2025-11-26 | Vercelプロジェクト作成、デプロイ完了 |
| ステップ10-3: カスタムドメイン設定 | ✅ 完了（DNS反映待ち） | 2025-11-26 | `yadopera.com`追加、DNS設定実施済み |

### 1.2 次のステップ

| ステップ | ステータス | 前提条件 | 所要時間 |
|---------|----------|---------|---------|
| ステップ10-4: Google Analytics設定 | ⏳ 準備完了 | `https://yadopera.com`が利用可能 | 30分 |
| ステップ10-5: HTMLに測定ID設定 | ⏳ 準備完了 | ステップ10-4完了 | 10分 |
| ステップ10-6: 動作確認 | ⏳ 準備完了 | ステップ10-5完了 | 10分 |

---

## 2. 前提条件の確認

### 2.1 必須前提条件

- ✅ **Vercelデプロイ完了**: ステップ10-2完了済み
- ✅ **カスタムドメイン設定完了**: ステップ10-3完了済み（DNS反映待ち）
- ⏳ **`https://yadopera.com`が利用可能**: DNS反映待ち（最大48時間）

### 2.2 DNS反映確認方法

1. **ブラウザでアクセス確認**
   - `https://yadopera.com` にアクセス
   - ページが正常に表示されることを確認

2. **VercelのDomains画面で確認**
   - Vercelダッシュボード → プロジェクト → Domains
   - `yadopera.com`のステータスが「Valid Configuration」になっていることを確認

3. **DNS反映タイムライン**
   - 通常: 数時間〜24時間
   - 最大: 48時間
   - 現在の状況: 2025-11-26に設定実施、明日午前中に確認予定

---

## 3. 実装済み内容の確認

### 3.1 Google Analytics 4コード実装状況

**ファイル**: `landing/index.html`

**実装箇所**:
- 26行目: Google Analytics 4のgtag.js読み込み
- 27-34行目: Google Analytics 4の初期化コード

**現在の状態**:
```html
<!-- Google Analytics 4 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());
    gtag('config', 'G-XXXXXXXXXX', {
        page_path: window.location.pathname,
    });
</script>
```

**プレースホルダー**: `G-XXXXXXXXXX`（2箇所）
- 26行目: gtag.jsのURL
- 31行目: gtag('config')の測定ID

### 3.2 イベントトラッキング実装状況

**実装済みイベント**: 10種類

1. **セクション閲覧** (`section_view`)
   - パラメータ: `section_name`, `section_title`
   - 実装: IntersectionObserver API使用

2. **CTAクリック** (`cta_click`)
   - パラメータ: `button_text`, `button_location`, `cta_type`
   - 実装: すべてのCTAボタンにイベントリスナー

3. **ナビゲーションクリック** (`navigation_click`)
   - パラメータ: `link_text`, `target_section`
   - 実装: ナビゲーションメニューのリンク

4. **外部リンククリック** (`external_link_click`)
   - パラメータ: `link_url`, `link_text`
   - 実装: すべての外部リンク

5. **説明会予約クリック** (`seminar_booking_click`)
   - パラメータ: `link_url`
   - 実装: Calendly/Googleカレンダーリンク（現在コメントアウト）

6. **PoCフォーム送信** (`poc_form_submit`)
   - パラメータ: `facility_name`, `location`, `foreign_guest_ratio`, `staff_count`
   - 実装: Formspreeフォーム送信時

7. **スクロール深度** (`scroll_depth`)
   - パラメータ: `depth_percent` (25, 50, 75, 90, 100)
   - 実装: スクロールイベントリスナー

8. **ページ滞在時間** (`page_time`)
   - パラメータ: `time_spent_seconds`
   - 実装: beforeunloadイベント

9. **モバイルメニュー操作** (`mobile_menu_toggle`)
   - パラメータ: `is_open` (true/false)
   - 実装: モバイルメニューボタンクリック

10. **ページビュー** (`page_view`)
    - パラメータ: `page_path`（自動）
    - 実装: Google Analytics 4の自動トラッキング

### 3.3 実装ファイル一覧

| ファイル | 内容 | ステータス |
|---------|------|----------|
| `landing/index.html` | Google Analytics 4コード実装 | ✅ 完了（プレースホルダー） |
| `landing/analytics-setup.md` | 設定ガイド | ✅ 作成済み |
| `docs/Phase0/Phase0_ステップ10_正しい実施順序.md` | 実施順序ドキュメント | ✅ 作成済み |

---

## 4. ステップ10-4の詳細手順

### 4.1 Google Analytics 4プロパティ作成

**所要時間**: 30分  
**前提条件**: `https://yadopera.com`が利用可能

**手順**:

1. **Google Analyticsにアクセス**
   - URL: https://analytics.google.com/
   - Googleアカウントでログイン

2. **プロパティ作成**
   - 「管理」→「プロパティを作成」をクリック
   - プロパティ名: 「やどぺら LP」
   - **ウェブサイトURL**: `https://yadopera.com`（実際のURL）
   - レポートのタイムゾーン: 「日本標準時」
   - 通貨: 「日本円 (¥)」
   - 「作成」をクリック

3. **データストリーム設定**
   - 「管理」→「データストリーム」をクリック
   - 「ウェブ」を選択
   - ウェブサイトURL: `https://yadopera.com`
   - ストリーム名: 「やどぺら LP」
   - 「ストリームを作成」をクリック

4. **測定ID取得**
   - データストリーム作成後、測定ID（`G-XXXXXXXXXX`形式）が表示される
   - 測定IDをコピー（後で使用）

**完了基準**:
- [ ] Google Analytics 4プロパティ作成完了
- [ ] データストリーム作成完了
- [ ] 測定ID取得済み（`G-XXXXXXXXXX`形式）

### 4.2 注意事項

- **Render.comのサービス作成は不要**: ランディングページはVercelにデプロイするため
- **実際のURLが必要**: プロパティ作成時に`https://yadopera.com`を入力する必要がある
- **測定IDの形式**: `G-`で始まる10文字の英数字（例: `G-ABC123XYZ`）

---

## 5. ステップ10-5の準備（HTMLに測定ID設定）

### 5.1 編集箇所

**ファイル**: `landing/index.html`

**編集箇所**: 2箇所
- 26行目: `G-XXXXXXXXXX` → 実際の測定ID
- 31行目: `G-XXXXXXXXXX` → 実際の測定ID

**編集例**:
```html
<!-- 変更前 -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
...
gtag('config', 'G-XXXXXXXXXX', {

<!-- 変更後（例: 測定IDが G-ABC123XYZ の場合） -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-ABC123XYZ"></script>
...
gtag('config', 'G-ABC123XYZ', {
```

### 5.2 コミット・プッシュ手順

```bash
# ファイル編集後
git add landing/index.html
git commit -m "Add Google Analytics measurement ID"
git push origin main
```

**Vercel自動再デプロイ**: プッシュ後、Vercelが自動で再デプロイ（1-2分）

---

## 6. ステップ10-6の準備（動作確認）

### 6.1 確認項目

1. **ページ表示確認**
   - `https://yadopera.com` にアクセス
   - ページが正常に表示されることを確認

2. **開発者ツールでの確認**
   - ブラウザの開発者ツール（F12）を開く
   - Networkタブで `gtag/js` のリクエストを確認
   - ステータスコード200（成功）を確認

3. **Google Analyticsリアルタイムレポート確認**
   - Google Analyticsダッシュボードにアクセス
   - 「レポート」→「リアルタイム」→「概要」を選択
   - アクセスが記録されていることを確認

### 6.2 トラブルシューティング

**イベントが記録されない場合**:

1. **ブラウザの拡張機能を確認**
   - 広告ブロッカーがGAをブロックしていないか確認
   - プライバシー拡張機能を一時的に無効化

2. **測定IDが正しいか確認**
   - `G-XXXXXXXXXX`形式であることを確認
   - コピー&ペーストで誤字がないか確認

3. **Google Analytics 4のリアルタイムレポートで確認**
   - リアルタイムレポートでイベントが表示されるか確認
   - 表示されない場合は、実装に問題がある可能性

4. **ブラウザのコンソールでエラーを確認**
   - 開発者ツール（F12）でエラーがないか確認

---

## 7. 実装済みイベントトラッキングの詳細

### 7.1 イベント一覧とパラメータ

| イベント名 | パラメータ | 実装箇所 | 用途 |
|-----------|-----------|---------|------|
| `page_view` | `page_path` | 自動 | ページビュー追跡 |
| `section_view` | `section_name`, `section_title` | IntersectionObserver | セクション閲覧率 |
| `cta_click` | `button_text`, `button_location`, `cta_type` | CTAボタン | CTAクリック率 |
| `navigation_click` | `link_text`, `target_section` | ナビゲーションメニュー | ナビゲーション使用状況 |
| `external_link_click` | `link_url`, `link_text` | 外部リンク | 外部リンククリック率 |
| `seminar_booking_click` | `link_url` | 説明会予約リンク | 説明会予約率（現在コメントアウト） |
| `poc_form_submit` | `facility_name`, `location`, `foreign_guest_ratio`, `staff_count` | PoCフォーム | PoC応募コンバージョン |
| `scroll_depth` | `depth_percent` | スクロールイベント | エンゲージメント測定 |
| `page_time` | `time_spent_seconds` | beforeunload | 滞在時間測定 |
| `mobile_menu_toggle` | `is_open` | モバイルメニュー | モバイルUX測定 |

### 7.2 カスタムレポート推奨設定

**PoC応募コンバージョン**:
- イベント: `poc_form_submit`
- 目標: PoC応募完了
- 用途: PoC応募率の測定

**CTAクリック率**:
- イベント: `cta_click`
- セグメント: `cta_type = apply`
- 用途: CTA効果測定

**セクション閲覧率**:
- イベント: `section_view`
- セクション: 各セクションID
- 用途: コンテンツエンゲージメント測定

---

## 8. 関連ドキュメント

### 8.1 実装ガイド

- **`landing/analytics-setup.md`**: Google Analytics設定の詳細ガイド
- **`docs/Phase0/Phase0_ステップ10_正しい実施順序.md`**: ステップ10の正しい実施順序
- **`docs/Phase0/Phase0_次のステップ_推奨案.md`**: 次のステップの推奨案

### 8.2 参考資料

- [Google Analytics 4 ドキュメント](https://developers.google.com/analytics/devguides/collection/ga4)
- [GA4 イベントトラッキング](https://developers.google.com/analytics/devguides/collection/ga4/events)

---

## 9. 実施タイムライン

### 9.1 最優先フロー（DNS反映確認後）

```
1. DNS反映確認（5分）
   ↓
2. ステップ10-4: Google Analytics設定（30分）
   ↓
3. ステップ10-5: HTMLに測定ID設定（10分）
   ↓
4. ステップ10-6: 動作確認（10分）
```

**合計**: 約55分（DNS反映確認後）

### 9.2 注意事項

- **DNS反映待ち**: 最大48時間かかる場合がある
- **測定IDの管理**: 測定IDは安全に管理（Git管理は問題なし、公開情報のため）
- **Vercel自動再デプロイ**: プッシュ後、自動で再デプロイされる

---

## 10. まとめ

### 10.1 準備状況

- ✅ **Google Analytics 4コード実装**: 完了（プレースホルダー）
- ✅ **イベントトラッキング実装**: 10種類完了
- ✅ **設定ガイド**: 作成済み
- ⏳ **DNS反映待ち**: `https://yadopera.com`が利用可能になるまで待機

### 10.2 次のアクション

1. **DNS反映確認**（5分）
   - `https://yadopera.com` にアクセスして確認
   - VercelのDomains画面で「Valid Configuration」を確認

2. **ステップ10-4実施**（30分）
   - Google Analytics 4プロパティ作成
   - 測定ID取得

3. **ステップ10-5実施**（10分）
   - HTMLに測定ID設定
   - コミット・プッシュ

4. **ステップ10-6実施**（10分）
   - 動作確認
   - リアルタイムレポート確認

**準備完了**: すべての準備が整っており、DNS反映確認後、すぐに実施可能です。

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-26  
**Status**: 調査分析完了、準備完了（DNS反映待ち）

