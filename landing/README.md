# やどぺら ランディングページ

PoC募集用のランディングページです。

## 構成

- `index.html`: メインのランディングページ（12セクション構成）
- `vercel.json`: Vercelデプロイ設定

## セクション構成

1. ヒーローセクション（メインコピー + CTA）
2. 課題提起セクション（宿側の悩み + ゲスト側の遠慮）
3. コンセプトセクション（「無人化ではなくホスピタリティ拡張」）
4. 3つの価値セクション
5. 仕組みセクション（QR3ステップ）
6. 導入効果セクション（年間¥401,500削減の試算）
7. PoC募集セクション（応募フォーム含む）
8. 選ばれる理由セクション（6つの差別化ポイント）
9. 料金セクション（正式版プラン）
10. FAQセクション（7項目）
11. 運営者情報セクション
12. 最終CTAセクション

## 技術スタック

- HTML5
- Tailwind CSS（CDN）
- Vanilla JavaScript

## デプロイ

### Vercelでのデプロイ

1. Vercelアカウントにログイン
2. 新しいプロジェクトを作成
3. `landing/`ディレクトリを選択
4. カスタムドメイン設定（`tabipera.com`）

### ローカルでの確認

```bash
# シンプルなHTTPサーバーで起動
cd landing
python3 -m http.server 8000
# または
npx serve .
```

ブラウザで `http://localhost:8001` にアクセス

**現在のローカルURL**: http://localhost:8001

**注意**: ポート8000はbackend（FastAPI）が使用しているため、ランディングページはポート8001で起動しています。

## フォーム連携

現在、フォーム送信はプレースホルダー実装です。実際の運用では以下のいずれかに接続してください：

1. **Google Forms**: フォームをGoogle Formsで作成し、`action`属性にURLを設定
2. **Formspree**: 無料のフォームサービス（https://formspree.io/）
3. **バックエンドAPI**: やどぺらのバックエンドAPIに接続

### Formspreeの例

```html
<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
  <!-- フォームフィールド -->
</form>
```

### Google Formsの例

1. Google Formsでフォームを作成
2. 「送信」ボタンの右側の「...」をクリック
3. 「HTMLを取得」を選択
4. `action`属性のURLをコピーして`<form>`タグに設定

## カスタマイズ

### 色の変更

Tailwind CSSのカスタムクラスを使用しています。主な色は：
- オレンジ系: `orange-600`, `orange-700`
- グレー系: `gray-50`, `gray-100`, `gray-700`

変更する場合は、`index.html`内のクラス名を変更してください。

### コンテンツの更新

`index.html`を直接編集してコンテンツを更新してください。

## 注意事項

- フォーム送信機能は実際のサービスに接続する必要があります
- デモ動画は後で追加可能（YouTube埋め込み）
- OGP画像は後で追加推奨
- **Google Analytics**: 実装済み（`G-XXXXXXXXXX`を実際の測定IDに置き換える必要があります）
  - 詳細は `analytics-setup.md` を参照してください

## 関連ドキュメント

- `docs/poc-promotion-requirements.md`: PoCプロモーション要件書
- `docs/yadopera-v03-summary.md`: 要約定義書

