# Phase 0 ステップ10-7: DNS設定 緊急修正手順

**作成日**: 2025年11月27日  
**目的**: GitHub PagesのDNS設定エラーを迅速に修正  
**エラー**: `Domain does not resolve to the GitHub Pages server`

---

## 問題の状況

GitHub Pagesのカスタムドメイン設定で以下のエラーが表示されています：

```
DNS check unsuccessful
Both yadopera.com and its alternate name are improperly configured
Domain does not resolve to the GitHub Pages server
```

これは、DNS設定がまだGitHub Pagesのサーバーを指していないことを示しています。

---

## 迅速な解決手順

### ステップ1: ムームードメインでDNS設定を確認・修正

1. **ムームードメイン管理画面にアクセス**
   - https://muumuu-domain.com/ にログイン

2. **ドメイン管理画面を開く**
   - `yadopera.com` を選択
   - **「DNS設定」** または **「DNSレコード設定」** をクリック

3. **現在のDNSレコードを確認**
   - Aレコード: `@` → `216.198.79.1`（VercelのIPアドレス）が残っている場合は削除
   - CNAMEレコード: `@` → `kurinobu.github.io` が設定されているか確認

4. **CNAMEレコードを設定（または修正）**
   - レコードタイプ: `CNAME`
   - ホスト名: `@`（または空欄）
   - 値: `kurinobu.github.io`
   - TTL: 3600（デフォルト）

5. **保存**

### ステップ2: DNS設定の反映を待つ

- **反映時間**: 通常5-30分（最大1時間）
- **確認方法**:
  ```bash
  dig yadopera.com +short
  # または
  nslookup yadopera.com
  ```
  - 正しく設定されていれば、`kurinobu.github.io` が返ってきます

### ステップ3: GitHub Pagesで再確認

1. Settings → Pages に戻る
2. カスタムドメイン設定を再確認
3. エラーが解消されるまで待つ（DNS反映後）

---

## 代替案: 一時的にGitHub PagesのデフォルトURLを使用

DNS設定の反映を待つ間、一時的にGitHub PagesのデフォルトURLを使用することもできます：

- URL: `https://kurinobu.github.io/yadopera/`

DNS設定が反映されたら、`yadopera.com` に切り替えます。

---

## 重要なポイント

1. **Aレコードを削除**: VercelのIPアドレス（216.198.79.1）へのAレコードは削除してください
2. **CNAMEレコードを設定**: `@` → `kurinobu.github.io` のCNAMEレコードを設定してください
3. **反映を待つ**: DNS設定の反映には時間がかかります（最大1時間）

---

## 確認コマンド

DNS設定が正しく反映されているか確認：

```bash
# 方法1: digコマンド
dig yadopera.com +short

# 方法2: nslookupコマンド
nslookup yadopera.com

# 方法3: オンラインツール
# https://dnschecker.org/
# https://www.whatsmydns.net/
```

正しく設定されていれば、`kurinobu.github.io` が返ってきます。

---

**Document Version**: v1.0  
**Author**: Air  
**Last Updated**: 2025-11-27  
**Status**: 緊急修正手順完成


