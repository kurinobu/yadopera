# PR・Vercel・失敗チェックの説明と、画面でやること

**Vercel は絶対厳禁であり、即座に排除する。** このプロジェクトで Vercel を使用・表示・連携することは一切許されない。選択の余地はない。Phase 1（2025-11-28）で決定済み。**今まで Vercel で成功したことは一度もなく、失敗は数多く、いつも邪魔をされて先に進めないのが Vercel である。即座に排除する。**（`docs/Phase1/Phase1_引き継ぎ書.md` 11.2、`docs/開発規約/重大失態再発防止策.md`）

---

## 0.5 タスク完了までの順序（必ずこの順で行う）

| 順 | やること | 説明 |
|----|----------|------|
| **①** | **コミット＆プッシュ** | いまの変更（この doc の更新・`landing/vercel.json` 削除）を `feature/lp-v1-production` にコミットし、`git push` する。**先にここまでやらないと、PR が古いままになり「次に進む」ができない。** |
| **②** | （任意）Vercel 完全排除 | 必要なら §2.1 の **方法B（プロジェクト削除）** を Vercel ダッシュボードで実行。Disconnect 済みなら省略可。 |
| **③** | PR 確認・マージで Step 6 完了 | §4 のとおり失敗チェック「Staging Deploy / Run Tests」を確認し、LP と無関係なら §5 のとおり **Merge pull request** → **Confirm merge** で develop にマージ。これで Step 6（develop 確認まで）完了。 |

**結論: コミット＆プッシュが先。そのあと「次に進む」（Vercel 方法B の有無 → PR マージ）。**

---

## 0. なぜ PR に Vercel が出ているか（あなたの意思に反する理由）

**結論: コードで「また使い始めた」のではない。昔、Vercel にこのリポジトリを接続したまま、解除していないため。**

- **方針（すでに決定済み）**: **Vercel は絶対厳禁。** 使用・PR への表示・GitHub 連携のいずれも禁止。
- **いま起きていること**: PR を出すと Vercel がビルドして PR にコメント・チェックが出る。これは方針違反である。
- **理由**: **Vercel のサイト（vercel.com）側で、「この GitHub リポジトリ（kurinobu/yadopera）を監視する」連携が残っている。** 厳禁としたときに、**Vercel ダッシュボードでその連携を外す（またはプロジェクトを削除する）作業をしていなかった**ため、PR のたびに Vercel が自動で動いている。
- 以下「Vercel を PR に出さないようにする手順」は、**Vercel を絶対に使わない状態にするため**の必須手順である。Vercel 公式ドキュメントに基づく操作のみを記載する（憶測は含まない）。出典: [Git settings](https://vercel.com/docs/projects/project-configuration/git-settings)、[Managing projects](https://vercel.com/docs/projects/managing-projects)。

---

## 1. PR（Pull Request）とは（一行）

**「このブランチの変更を、develop に取り込んでよいか」を GitHub に依頼するためのページ。** 宣伝ではない。

---

## 2. Vercel とは（一行＋このリポの話）

**Vercel = ウェブサイトを置いてプレビューURLを出してくれるサービス。**  
**このプロジェクトでは絶対厳禁。** 使用・PR への表示・連携は一切禁止。選択の余地はない。PR に Vercel が出るのは、上記のとおり **Vercel 側の GitHub 連携が残っているため**であり、その連携を外す（またはプロジェクトを削除する）ことが必須である。本番 LP は **GitHub Pages** のみ使用する。

---

## 2.1 Vercel を PR に表示させない手順（公式ドキュメントに基づく）

**出典**:  
- [Git settings - Disconnect your Git repository](https://vercel.com/docs/projects/project-configuration/git-settings)  
- [Managing projects - Deleting a project](https://vercel.com/docs/projects/managing-projects)

### 方法A: GitHub 連携だけ解除する（プロジェクトは残す）

1. ブラウザで **https://vercel.com/dashboard** を開く。
2. 必要ならログインする。**チーム**を使っている場合は、画面上部のチーム切り替えで、対象のチームを選ぶ。
3. **ダッシュボード**のプロジェクト一覧から、このリポジトリ（kurinobu/yadopera）に紐づいているプロジェクト（例: **yadopera-landing**）の **名前をクリック**して、そのプロジェクトの画面を開く。
4. 左サイドバーで **「Settings」** をクリックする。
5. Settings の左サイドバー（またはサブメニュー）で **「Git」** をクリックする。  
   （公式: "Open Settings in the sidebar and select Git" / "select the Git menu item from your project settings page"）
6. ページ内の **「Connected Git Repository」** のブロックを探す。
7. そのブロック内の **「Disconnect」** ボタンをクリックする。  
   （公式: "Under Connected Git Repository, select the Disconnect button."）
8. 確認ダイアログがあれば、内容を読んでから **確定（OK / Confirm 等）** をクリックする。

**Disconnect の直後〜次にやること**

9. 同じ Vercel の **Settings → Git** の画面をそのまま見る。  
   - **「Connected Git Repository」** がなくなり、代わりに **「Connect Git Repository」** やリポジトリを選ぶ UI が出ていれば、切断できている。

**確認（PR に Vercel が出なくなったか）**

10. GitHub の **PR #1**（https://github.com/kurinobu/yadopera/pull/1）を開く。  
11. 画面上方の **「Checks」** タブをクリックする。  
12. 一覧に **「Vercel」** や **「Vercel Preview Comments」** が **もう無い**、または **これ以降の新しいチェック実行では Vercel が動いていない** ことを確認する。  
    （すでに出ている過去の Vercel コメントは残ることがある。新規で PR を更新するか、新 PR を出したときに Vercel が動かなければ成功。）  
13. 必要なら、**PR に空コミットを push する**（例: `git commit --allow-empty -m "chore: trigger check" && git push`）と、チェックが再実行される。そのあと **Checks** に Vercel が現れなければ、連携解除の確認完了。

これで、そのプロジェクトは GitHub の push/PR に反応しなくなる。PR に Vercel のコメント・チェックは出なくなる。

**補足（Disconnect 後にまだ Vercel が PR に出る場合）**: PR に表示されている Vercel のコメントや「2 successful checks」の Vercel は、**Disconnect より前に実行された過去のチェック結果**です。GitHub は一度出たチェック結果を消さないため、その PR の Conversation や Checks には残ります。Disconnect が効いていれば、**このあと新しい push をしたとき**には Vercel は動かず、新しいチェック一覧に Vercel は現れません。確認するには、PR のブランチに空コミットを push し、Checks タブで「新しく走ったチェックに Vercel が含まれていないか」を見てください。

### 方法B: プロジェクトごと削除する

1. ブラウザで **https://vercel.com/dashboard** を開く。
2. 必要ならログインする。**チーム**を使っている場合は、画面上部のチーム切り替えで、対象のチームを選ぶ。
3. **ダッシュボード**のプロジェクト一覧から、このリポジトリに紐づいているプロジェクト（例: **yadopera-landing**）の **名前をクリック**して、そのプロジェクトの画面を開く。
4. 左サイドバーで **「Settings」** をクリックする。
5. Settings の左サイドバー（またはサブメニュー）で **「General」** をクリックする。  
   （公式: "At the bottom of the General page" に Delete があるため、General を開く）
6. **General ページのいちばん下までスクロール**する。
7. **「Delete Project」** セクションを探す。
8. そのセクション内の **「Delete」** ボタンをクリックする。  
   （公式: "Click the Delete button"）
9. 表示された **「Delete Project」** ダイアログで、指示に従い **プロジェクト名（とプロンプト）を入力**する。
10. ダイアログ内の **「Continue」** ボタンをクリックする。  
    （公式: "confirm that you'd like to delete the project by entering the project name and prompt. Then, click the Continue button"）

これでプロジェクトが削除され、PR に Vercel は一切出なくなる。

**Vercel について「使うか・使わないか」の選択は存在しない。絶対厳禁で決まっている。即座に排除する。**

**リポジトリ内の排除**: `landing/vercel.json`（Vercel 用設定）は削除済み。Vercel を即座に排除する方針に従い、コードベースに Vercel の設定を残さない。

※ 画面上のラベルが英語の場合は、上記の「Settings」「Git」「General」「Connected Git Repository」「Disconnect」「Delete Project」「Delete」「Continue」は同じ英語表記で表示される。

---

## 3. 失敗しているチェック「Staging Deploy / Run Tests」とは

GitHub Actions の **「Staging Deploy」** ワークフローが、PR のたびに動いている。  
その中の **「Run Tests」** ジョブ = **backend の pytest（バックエンドのテスト）** を実行している。  
LP の変更（landing/ や docs/）とは無関係。**もともと develop 向けのテスト** が 1 つ失敗している状態。

---

## 4. 失敗理由を実際の画面で確認する手順（順番どおり）

いま開いている **PR #1 のページ**（`https://github.com/kurinobu/yadopera/pull/1`）で、次を順にやる。

1. **PR の本文エリア**（タイトル「lp-v1: Step 6 は develop 確認まで…」の下）で、  
   **「Some checks were not successful」** または **「1 failing」** と書いてあるブロックを探す。

2. そのブロックのなかに、  
   **「Staging Deploy / Run Tests (pull_request)」** の行がある。  
   その行の **右端の「Details」** をクリックする。  
   （「Details」が無い場合は、その行自体をクリックする。）

3. **GitHub の Actions ページ** に飛ぶ。  
   「Staging Deploy」のワークフロー実行が開き、**ジョブ一覧**（Run Tests など）が出る。

4. **「Run Tests」** ジョブ（赤い × が付いている）をクリックする。

5. 左側に **ステップの一覧**（Checkout code, Setup Python, Install dependencies, Run tests with coverage, …）、  
   右側に **そのステップのログ** が出る。  
   **「Run tests with coverage」** をクリックする。

6. 右側のログを **下までスクロール** する。  
   **赤い文字や FAILED、Error** が出ている行が、失敗の原因。  
   その数行上から下までを読めば「何のテストがなぜ落ちたか」が分かる。

ここまでで「次のアクション」は終わり。  
失敗内容が分かったら、  
- LP の変更とは無関係なら「この PR はマージしてよい」と判断して **Merge pull request** で develop にマージして Step 6 完了、  
- 直すなら backend のテスト修正を別コミットしてから再度 PR を更新、  
のどちらかになる。

---

## 5. Step 6 を完了させる操作（マージする場合）

失敗チェックを「無視してマージしてよい」と判断した場合：

1. PR #1 のページに戻る（`https://github.com/kurinobu/yadopera/pull/1`）。
2. 下の方の **緑の「Merge pull request」** をクリック。
3. 出てきた **「Confirm merge」** をクリック。

これで feature/lp-v1-production が develop に取り込まれ、**Step 6（develop 確認まで）完了**。
