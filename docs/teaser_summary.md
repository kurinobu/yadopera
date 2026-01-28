# yadopera ティザーサイト用 要約定義書  
（正式ローンチ前・情報最小化版）

---

## 1. ティザーサイトの目的

本ティザーサイトの目的は、  
**yadoperaを売ることではない。**

- サービス開始前に関心を持った宿泊施設に  
  「あとで正式に確認したい」という保留フラグを立ててもらう
- 本番LP公開前に、思想・方向性を正しく伝える
- メールアドレスは目的ではなく、副産物とする

---

## 2. 想定公開期間

- PoC進行中 〜 正式ローンチ直前まで
- 想定：2026年2月〜4月初旬

---

## 3. 想定ターゲット

### 主ターゲット
- ゲストハウス・ホステル
- スタッフ1〜10名規模
- 常時フロントに人がいるわけではない宿泊施設
- 説明対応・問い合わせ対応が負担になっている施設

### 副ターゲット
- 地方の小規模宿泊施設
- 将来的に外国人比率が増える可能性のある施設
- ビジネスホテル・宿坊などの試験導入検討層

---

## 4. ティザーサイトで「伝えること」

### 4-1. 一番伝えるべきメッセージ

> フロントに人がいない時間、  
> 説明を止めない。

- 夜間限定ではない
- 無人・半無人時間帯を前提とした設計
- スタッフの代わりに接客するサービスではない

---

### 4-2. サービスの立ち位置

- yadoperaは自動接客ツールではない
- 説明を継続するための一次対応の仕組み
- 判断や責任は人に戻す前提

---

### 4-3. ティザーで触れてよい内容

- サービスの思想・前提
- 想定している宿泊施設像
- Freeプランが存在すること（詳細は出さない）
- 正式ローンチ時期（目安）

---

## 5. ティザーサイトで「出さないこと」

- 機能一覧
- 価格詳細
- 導入効果の数値
- 補助金・制度説明
- 競合比較
- デモ画面

---

## 6. ティザーサイトの構成（ページ内）

1. ファーストビュー  
   - キャッチコピー  
   - サブコピー  
   - リリース予定時期

2. 対象宿泊施設の明示  
   - 自分事判定用の箇条書き

3. サービスの考え方  
   - やらないことを含めた説明

4. ティザー登録フォーム  
   - 「サービス開始時に1通だけ連絡する」  
   - 営業しないことの明記

5. PoC進行中の補足（任意・控えめ）

---

## 7. メール登録の扱い

- 登録目的は「サービス開始連絡のみ」
- 正式ローンチ時に **1通だけ送信**
- メルマガ・営業メールには使用しない

---

## 8. 成功指標（KPI）

- 登録数ではなく「登録率」
- 流入に対して  
  「登録する価値がある」と判断されたか

---

## 9. 本番LPへの移行方針

- ティザー登録者には本番LP公開時に1通だけ通知
- ティザーサイトは本番LP公開後に非公開またはリダイレクト
- ティザーで使用したコピーは、本番LPで検証素材として再利用

---

## 10. 判断基準（このティザーは成功か？）

- 「売り込まれた」と感じさせていない
- 「現場を分かっていそう」と思われている
- 「余裕がある時にちゃんと見たい」と思わせている

---

## 補足

このティザーサイトは  
yadoperaというサービスの **温度感・思想・距離感** を  
誤解なく伝えるためのものである。

情報を出さないことは、  
不誠実ではなく、設計である。

参考構成
/
├── index.html          ← ティザー（当面ここ）
├── teaser/             ← 将来分離用（任意）
└── landing/
    └── index.html      ← PoC / 本番LP（非公開 or noindex）


参考ティザーサイト
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>YadOPERA｜小規模宿泊施設向け案内支援サービス（準備中）</title>
  <meta name="description" content="YadOPERAは、小規模宿泊施設の運営負担を軽くするための案内支援サービスです。現在サービス準備中。開始時に1通だけご案内します。" />

  <script src="https://cdn.tailwindcss.com"></script>

  <style>
    body { font-family: 'Noto Sans JP', sans-serif; }
  </style>
</head>
<body class="bg-gray-50 text-gray-800">

  <main class="min-h-screen flex items-center justify-center px-4">
    <div class="max-w-xl w-full bg-white shadow-md rounded-lg p-8">

      <h1 class="text-2xl md:text-3xl font-bold text-center mb-4">
        YadOPERA
      </h1>

      <p class="text-center text-gray-600 mb-6">
        小規模宿泊施設向け<br class="md:hidden">
        案内支援サービス
      </p>

      <div class="border-t border-b py-6 mb-6 text-sm leading-relaxed text-gray-700">
        <p class="mb-3">
          YadOPERAは、<br>
          スタッフが対応しきれない時間帯や、<br>
          「聞きづらさ」が生まれやすい場面での<br>
          <strong>宿泊施設の案内負担を軽くする</strong>ためのサービスです。
        </p>
        <p>
          現在、正式リリースに向けて準備を進めています。
        </p>
      </div>

      <p class="text-sm text-gray-600 mb-4 text-center">
        サービス開始時に<br>
        <strong>1通だけ</strong>ご連絡します
      </p>

      <form
        action="https://formspree.io/f/xxxxxxx"
        method="POST"
        class="space-y-4"
      >
        <div>
          <label class="block text-sm mb-1">メールアドレス</label>
          <input
            type="email"
            name="email"
            required
            class="w-full border rounded px-3 py-2 focus:outline-none focus:ring"
          />
        </div>

        <button
          type="submit"
          class="w-full bg-slate-800 text-white py-2 rounded hover:bg-slate-700 transition"
        >
          開始時に連絡を受け取る
        </button>
      </form>

      <p class="text-xs text-gray-500 mt-4 text-center">
        ※ 営業メールは送信しません<br>
        ※ 本通知は1回限りです
      </p>

    </div>
  </main>

</body>
</html>



推奨運用フロー
フェーズ1（今〜3月）

/ → ティザーHTML

/landing/ →

noindex

URL直打ち or 個別案内のみ

SNS・知人・検索流入はすべてティザーへ

フェーズ2（4月ローンチ直前）

ティザー登録者に 1通通知

/ を 本番LP に切替

ティザーHTMLは /teaser-closed.html 等で保存


補足（かなり重要）

「AI」「多言語」「自動化」
→ ティザーでは 1文字も使わない

数値（%・円）
→ 一切出さない

導入効果
→ 本番LPで初めて語る


メール文面例
Subject: 【yadopera】サービス提供を開始しました

yadopera にご関心をお寄せいただき、ありがとうございます。

ティザーサイトでご案内していた
宿泊施設向けサービス **yadopera** は、
本日より正式に提供を開始しました。

yadoperaは、
フロントに人がいない時間帯でも
「説明だけは止めない」ことを目的に設計した
宿泊施設向けの一次対応サービスです。

まずは **Freeプラン** からお使いいただけます。
合わなければ、使わなくても構いません。

▼ サービスページはこちら
[https://yadopera.com/](https://yadopera.com/)

※ 本メールは、ティザー登録時のお約束どおり
　**今回のご案内1通のみ**の送信です。
　今後こちらから営業メールをお送りすることはありません。

ご不明点があれば、サービスページ内のお問い合わせフォームから
いつでもご連絡ください。

yadopera
運営チーム
