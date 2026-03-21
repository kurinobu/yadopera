# やどぺら ランディングページ（`landing/`）

静的 HTML。**本番ドメイン `yadopera.com` は GitHub Pages**（`main` の本ディレクトリ）。**Vercel は使用しない**（プロジェクト大原則）。

## ブランチとファイルの役割（重要）

| ブランチ | 主なファイル | 役割 |
|----------|----------------|------|
| **`main`** | `index.html` | **`https://yadopera.com/` に公開される中身**（当面はティザー）。 |
| **`develop`** | `index.html` | **本番向け LP（LP v1.0 系）**の作業用。`main` と中身が分岐しうる。 |
| **`develop`** | `teaser-index.html` | **`main` の `index.html`（ティザー）と揃えるための差し替え元**（2026-03-21〜）。 |

**`develop` のみ push しても `yadopera.com` は更新されない。** ティザーを本番に反映するときは **`main` の `landing/index.html` を更新して push** すること。詳細: `docs/20260321_LPティザー_GitHubPages_ブランチとデプロイ不手際_記録.md`。

## 構成（参考）

- `index.html`: ブランチにより **ティザー（main）** または **本番LP（develop）**
- `teaser-index.html`: **develop のみ** — ティザー本文の正（`main` へ同期用）
- `poc-lp-20260120.html`: 旧 PoC 募集 LP のバックアップ
- `vercel.json`: **使用しない**（歴史的ファイル。削除済みバックアップあり）

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

## デプロイ（GitHub Pages）

1. **本番反映**: **`main`** にマージ（または `main` 上で直接コミット）し **`landing/**` を push**。
2. GitHub Actions **「Deploy to GitHub Pages」**（`.github/workflows/pages.yml`）が成功することを確認。
3. カスタムドメインはリポジトリの Pages 設定で既に `yadopera.com` が紐づいている想定。

### ローカルでの確認

```bash
cd landing
python3 -m http.server 8765
```

ブラウザで `http://127.0.0.1:8765/index.html`（**`develop` checkout 時は本番LP**、**`main` checkout 時はティザー**）または `http://127.0.0.1:8765/teaser-index.html`（**develop** のティザー差し替え元）。

**注意**: バックエンドがポート 8000 を使う場合があるため、`landing/` のプレビューは **空いているポート**（例: 8765）でよい。

## フォーム連携

ティザー等では **Formspree** を利用。接続先を変える場合は以下を参照：

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
- `docs/Summary/yadopera-v03-summary.md`: 要約定義書
- `docs/20260321_LPティザー_GitHubPages_ブランチとデプロイ不手際_記録.md`: 本番反映とブランチの注意

