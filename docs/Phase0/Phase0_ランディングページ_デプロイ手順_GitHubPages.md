# ランディングページ デプロイ手順（GitHub Pages）

**作成日**: 2025年11月27日  
**目的**: ランディングページをGitHub Pagesにデプロイし、Google Analyticsを設定する手順  
**背景**: Vercelの自動デプロイが機能しないため、GitHub Pagesに移行

---

## ⚠️ 重要なポイント

**ランディングページはRender.comとは完全に独立しています。**

- **ランディングページ**: GitHub Pagesにデプロイ（静的HTML）
- **本番アプリ**: Render.comにデプロイ（Phase 1 Week 4以降）
- **両者は別物で、ランディングページはPhase 0完了後すぐにデプロイ可能**

---

## デプロイ手順

### ステップ1: GitHub Pages設定

1. GitHubリポジトリにアクセス
   - https://github.com/kurinobu/yadopera

2. Settings → Pages を開く

3. Source設定
   - Source: `Deploy from a branch` を選択
   - Branch: `main` を選択
   - Folder: `/landing` を選択
   - 「Save」をクリック

4. カスタムドメイン設定
   - Custom domain: `yadopera.com` を入力
   - 「Save」をクリック

5. DNS設定変更
   - ムームードメインのDNS設定を変更
   - Aレコードを削除（`@` → `216.198.79.1`）
   - CNAMEレコードを追加（`@` → `kurinobu.github.io`）
   - または、GitHub Pagesが提供するIPアドレスを使用（Aレコード）

**注意**: GitHub Pagesのカスタムドメイン設定画面に表示されるDNS設定を確認してください。

### ステップ2: デプロイ確認

1. デプロイ完了を待つ（1-2分）

2. `https://yadopera.com` にアクセスして確認

3. ページが正常に表示されることを確認

### ステップ3: Google Analytics設定（既に完了）

**完了済み**:
- Google Analytics 4プロパティ作成完了
- 測定ID: `G-BE9HZ0XGH4`
- HTMLに測定ID設定完了（コミット: `4eddb00`）

**確認**:
- GitHub Pages移行後、自動デプロイで反映される
- `https://yadopera.com` でアクセス確認
- Google Analyticsのリアルタイムレポートで確認

---

## タイムライン

| ステップ | 時期 | 所要時間 |
|---------|------|---------|
| GitHub Pages設定 | Phase 0完了後、すぐに実施可能 | 5分 |
| カスタムドメイン設定 | デプロイ後 | 5分（DNS設定含む） |
| Google Analytics設定 | 既に完了 | - |
| 動作確認 | デプロイ後 | 10分 |
| **合計** | **Phase 0完了後、すぐに実施可能** | **約20分** |

---

## Render.comとの関係

### 混同しやすいポイント

❌ **誤解**: Render.comのサービス立ち上げを待たないとランディングページがデプロイできない

✅ **正解**: ランディングページはGitHub Pagesにデプロイするため、Render.comとは無関係

### 実際の関係

```
【ランディングページ（GitHub Pages）】
Phase 0完了 → すぐにデプロイ可能 → Google Analytics設定可能

【本番アプリ（Render.com）】
Phase 1 Week 4 → ステージング環境構築
Phase 4 → 本番環境構築

→ 両者は完全に独立している
```

---

## GitHub Pagesのメリット

### Vercelとの比較

| 項目 | GitHub Pages | Vercel |
|-----|-------------|--------|
| 設定時間 | 5分 | 30分+ |
| 自動デプロイ | ✅ 確実に機能 | ❌ 機能しない |
| カスタムドメイン | ✅ | ✅ |
| SSL証明書 | ✅ 自動 | ✅ 自動 |
| コスト | 無料 | 無料 |
| CLIログイン | 不要 | 必要（複雑） |

### メリット

1. **設定が簡単**: 5分で完了
2. **自動デプロイが確実**: GitHubへのプッシュで自動デプロイ
3. **既存のリポジトリで完結**: 新しいサービスを覚える必要がない
4. **時間を浪費しない**: 設定が簡単で、すぐに完了

---

## トラブルシューティング

### 問題: GitHub Pagesがデプロイされない

**解決策**:
- Settings → Pages で設定を確認
- Branch: `main`、Folder: `/landing` になっているか確認
- デプロイログを確認（Actionsタブ）

### 問題: カスタムドメインが設定できない

**解決策**:
- DNS設定が正しく行われているか確認
- GitHub Pagesのカスタムドメイン設定画面でDNS設定を確認
- CNAMEレコードが正しく設定されているか確認

### 問題: Google Analyticsが動作しない

**解決策**:
- 測定IDが正しく設定されているか確認（`G-BE9HZ0XGH4`）
- ブラウザの拡張機能（広告ブロッカー等）を確認
- Google Analyticsのリアルタイムレポートで確認

---

## 次のアクション

### すぐに実施可能（Phase 0完了後）

1. ✅ GitHub Pages設定（5分）
2. ✅ カスタムドメイン設定（5分）
3. ✅ Google Analytics設定（既に完了）
4. ✅ 動作確認（10分）
5. ✅ ランディングページ公開完了

### 後で実施（Phase 1以降）

- Render.comステージング環境構築（Phase 1 Week 4）
- Render.com本番環境構築（Phase 4）

---

## 参考資料

- **Vercel代替案検討**: `docs/Phase0/Phase0_Vercel代替案検討.md`
- **ホスティングサービス選択反省**: `docs/Phase0/Phase0_ホスティングサービス選択_反省と分析.md`
- **Google Analytics設定**: `docs/Phase0/Phase0_ステップ10-4_GoogleAnalytics設定_調査分析レポート.md`

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: GitHub Pages版デプロイ手順完成

