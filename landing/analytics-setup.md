# Google Analytics 4 セットアップガイド

## 1. Google Analytics 4 プロパティの作成

1. [Google Analytics](https://analytics.google.com/)にアクセス
2. 「管理」→「プロパティを作成」をクリック
3. プロパティ名: 「やどぺら LP」
4. レポートのタイムゾーン: 「日本標準時」
5. 通貨: 「日本円 (¥)」
6. 「次へ」をクリック
7. ビジネス情報を入力
8. 「作成」をクリック

## 2. 測定IDの取得

1. 「管理」→「データストリーム」をクリック
2. 「ウェブ」を選択
3. ウェブサイトURL: `https://tabipera.com`（または実際のURL）
4. ストリーム名: 「やどぺら LP」
5. 「ストリームを作成」をクリック
6. 測定ID（`G-XXXXXXXXXX`形式）をコピー

## 3. HTMLへの実装

`landing/index.html`の以下の部分を編集：

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

`G-XXXXXXXXXX`を実際の測定IDに置き換えてください。

## 4. 実装済みイベントトラッキング

以下のイベントが自動的にトラッキングされます：

### ページビュー
- **イベント名**: `page_view`（自動）
- **パラメータ**: `page_path`

### セクション閲覧
- **イベント名**: `section_view`
- **パラメータ**:
  - `section_name`: セクションID
  - `section_title`: セクションタイトル

### CTAクリック
- **イベント名**: `cta_click`
- **パラメータ**:
  - `button_text`: ボタンテキスト
  - `button_location`: ボタンがあるセクション
  - `cta_type`: `apply`（申し込む）または`other`

### ナビゲーションクリック
- **イベント名**: `navigation_click`
- **パラメータ**:
  - `link_text`: リンクテキスト
  - `target_section`: 遷移先セクションID

### 外部リンククリック
- **イベント名**: `external_link_click`
- **パラメータ**:
  - `link_url`: リンクURL
  - `link_text`: リンクテキスト

### 説明会予約クリック
- **イベント名**: `seminar_booking_click`
- **パラメータ**:
  - `link_url`: カレンダーリンクURL

### PoCフォーム送信
- **イベント名**: `poc_form_submit`
- **パラメータ**:
  - `facility_name`: 施設名
  - `location`: 所在地
  - `foreign_guest_ratio`: 外国人ゲスト比率
  - `staff_count`: スタッフ数

### スクロール深度
- **イベント名**: `scroll_depth`
- **パラメータ**:
  - `depth_percent`: 25, 50, 75, 90, 100

### ページ滞在時間
- **イベント名**: `page_time`
- **パラメータ**:
  - `time_spent_seconds`: 滞在秒数

### モバイルメニュー操作
- **イベント名**: `mobile_menu_toggle`
- **パラメータ**:
  - `is_open`: `true`/`false`

## 5. Google Analytics 4での確認方法

1. Google Analyticsダッシュボードにアクセス
2. 「レポート」→「リアルタイム」でリアルタイムデータを確認
3. 「レポート」→「エンゲージメント」→「イベント」でイベントデータを確認

## 6. カスタムレポートの作成（推奨）

以下のカスタムレポートを作成することを推奨します：

### PoC応募コンバージョン
- **イベント**: `poc_form_submit`
- **目標**: PoC応募完了

### CTAクリック率
- **イベント**: `cta_click`
- **セグメント**: `cta_type = apply`

### セクション閲覧率
- **イベント**: `section_view`
- **セクション**: 各セクションID

## 7. トラブルシューティング

### イベントが記録されない場合

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

## 8. プライバシーポリシーへの記載

Google Analytics使用をプライバシーポリシーに記載する必要があります。

例：
```
本サイトでは、Google Analyticsを使用してアクセス解析を行っています。
Google AnalyticsはCookieを使用してデータを収集します。
データは匿名で収集され、個人を特定するものではありません。
```

## 参考リンク

- [Google Analytics 4 ドキュメント](https://developers.google.com/analytics/devguides/collection/ga4)
- [GA4 イベントトラッキング](https://developers.google.com/analytics/devguides/collection/ga4/events)


