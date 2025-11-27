# Phase 0 ステップ10-7: Vercel後処理手順

**作成日**: 2025年11月27日  
**目的**: GitHub Pages移行完了後のVercelの処理  
**背景**: VercelからGitHub Pagesに移行完了

---

## Vercelの処理オプション

### オプション1: Vercelプロジェクトを削除（推奨）

**メリット**:
- ✅ 不要なプロジェクトを整理できる
- ✅ 混乱を避けられる
- ✅ カスタムドメインの設定が自動で削除される

**手順**:
1. Vercelダッシュボードにアクセス: https://vercel.com/dashboard
2. プロジェクト「yadopera-landing」を選択
3. Settings → General → Delete Project
4. プロジェクト名を入力して削除を確認

### オプション2: Vercelプロジェクトをそのまま残す

**メリット**:
- ✅ バックアップとして残せる
- ✅ 将来的にVercelに戻す可能性がある場合

**デメリット**:
- ⚠️ カスタムドメインの設定が残る（DNS設定と競合する可能性）
- ⚠️ 混乱の原因になる可能性

**推奨**: オプション1（削除）を推奨します。

---

## カスタムドメインの処理

### 重要: カスタムドメイン設定を削除

Vercelにカスタムドメイン（`yadopera.com`）が設定されている場合、削除する必要があります：

1. Vercelプロジェクトの Settings → Domains
2. `yadopera.com` を削除
3. または、プロジェクトを削除すると自動で削除されます

---

## 次のステップ

Vercelの処理後、以下を実施：

1. **ステップ10-6: 動作確認**（約10分）
   - `https://yadopera.com` でアクセス確認
   - Google Analyticsのリアルタイムレポートで確認
   - 測定ID `G-BE9HZ0XGH4` が正しく動作しているか確認

2. **Phase 0完了確認**
   - すべてのステップが完了したことを確認
   - Phase 1（MVP開発）の準備を開始

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: Vercel後処理手順完成

