# Phase1 / Phase2  
## PWAインストール後 起動時404エラー  
### 調査分析報告書 兼 推奨修正案

---

## 1. 本書の目的

本書は、YadOPERA において発生している  
**「PWAインストール後、ホーム画面アイコン起動時に404エラーが発生する問題」**  
について、

- 憶測を完全に排除し
- 事実と因果関係のみから
- 根本原因を特定し
- 再発しない恒久的な修正案を提示する

ことを目的とする。

---

## 2. 結論サマリー（最重要）

**原因は1点に確定できる。**

PWA起動時、Vue Router のガードや保存処理が実行される前に  
ルート `/` が「NotFound（404）」として確定している。

---

## 3. 根本原因

- `/` ルートに Error404 コンポーネントを直接割り当てている
- Vue Router 初期遷移時に即404が確定
- ガード・保存処理が一切実行されない

---

## 4. 推奨修正案

### 4.1 `/` を PWAブート専用ルートに変更

```ts
{
  path: '/',
  name: 'PWABoot',
  component: () => import('@/views/PWABoot.vue'),
}
```

### 4.2 PWABoot.vue

```ts
<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { isValidFacilityId } from '@/utils/validation'

const router = useRouter()

onMounted(() => {
  const last = localStorage.getItem('last_facility_url')

  if (last) {
    const match = last.match(/^\/f\/([^\/]+)/)
    if (match && isValidFacilityId(match[1])) {
      router.replace(last)
      return
    }
  }
  router.replace({ name: 'NotFound' })
})
</script>
```

### 4.3 404ルートは最後に定義

```ts
{
  path: '/:pathMatch(.*)*',
  name: 'NotFound',
  component: () => import('@/views/Error404.vue')
}
```

---

## 5. 最終結論

本問題は PWA や Safari の問題ではなく  
**Vue Router の初期遷移設計ミス**である。

---

Document Version: 1.0
