# Phase 1: ステップ2 カテゴリ別内訳グラフ問題 完全調査分析レポート

**作成日**: 2025年12月4日  
**実施者**: Auto (AI Assistant)  
**対象**: カテゴリ別内訳グラフが全て赤色で表示される問題の完全調査分析  
**状態**: 🔴 **根本原因特定完了**

---

## 1. 問題の概要

### 1.1 報告された問題

**問題**: グラフが全て赤色（100%）で表示される

**表示結果**:
```
カテゴリ別内訳
過去7日間のメッセージで使用されたFAQのカテゴリ集計

Basic: 2件
Facilities: 12件
Location: 1件
Trouble: 1件
合計: 16件
```

**問題点**:
- ⚠️ **グラフが全て赤色のみ**: カテゴリ別に色分けされていない
- ✅ **数値は正しく表示**: カテゴリ別の件数は正しく表示されている

### 1.2 期待される動作

各カテゴリが異なる色で表示されるべき:
- Basic (2件): 青色 (`#3b82f6`) - 約12.5%
- Facilities (12件): 緑色 (`#10b981`) - 約75%
- Location (1件): 黄色 (`#f59e0b`) - 約6.25%
- Trouble (1件): 赤色 (`#ef4444`) - 約6.25%

---

## 2. SVGエレメントの詳細分析

### 2.1 実際のSVGエレメント

**提供されたSVGエレメント**:
```html
<svg width="200" height="200" class="transform -rotate-90">
  <!-- 背景円 -->
  <circle cx="100" cy="100" r="80" fill="none" stroke="#e5e7eb" stroke-width="20" />
  
  <!-- セグメント1: Basic (青色) -->
  <circle cx="100" cy="100" r="80" fill="none" stroke="#3b82f6" stroke-width="20" 
          stroke-dasharray="502.6548245743669" stroke-dashoffset="439.822971502571" />
  
  <!-- セグメント2: Facilities (緑色) -->
  <circle cx="100" cy="100" r="80" fill="none" stroke="#10b981" stroke-width="20" 
          stroke-dasharray="502.6548245743669" stroke-dashoffset="62.83185307179588" />
  
  <!-- セグメント3: Location (黄色) -->
  <circle cx="100" cy="100" r="80" fill="none" stroke="#f59e0b" stroke-width="20" 
          stroke-dasharray="502.6548245743669" stroke-dashoffset="31.41592653589794" />
  
  <!-- セグメント4: Trouble (赤色) -->
  <circle cx="100" cy="100" r="80" fill="none" stroke="#ef4444" stroke-width="20" 
          stroke-dasharray="502.6548245743669" stroke-dashoffset="0" />
</svg>
```

### 2.2 計算値の検証

**circumference（円周）**: `2 * Math.PI * 80 = 502.6548245743669` ✅ 正しい

**各セグメントの計算**:
- **Basic (2件 / 16件 = 12.5%)**:
  - `dashLength = 502.6548245743669 * 0.125 = 62.83185307179586`
  - `offset = 502.6548245743669 - (0 + 62.83185307179586) = 439.822971502571` ✅
  
- **Facilities (12件 / 16件 = 75%)**:
  - `dashLength = 502.6548245743669 * 0.75 = 376.9911184307752`
  - `offset = 502.6548245743669 - (62.83185307179586 + 376.9911184307752) = 62.83185307179588` ✅
  
- **Location (1件 / 16件 = 6.25%)**:
  - `dashLength = 502.6548245743669 * 0.0625 = 31.41592653589793`
  - `offset = 502.6548245743669 - (439.822971502571 + 31.41592653589793) = 31.41592653589794` ✅
  
- **Trouble (1件 / 16件 = 6.25%)**:
  - `dashLength = 502.6548245743669 * 0.0625 = 31.41592653589793`
  - `offset = 502.6548245743669 - (471.238898038469 + 31.41592653589793) = 0` ✅

**問題点**: 計算値は正しいが、**セグメントの順序と重なりが問題**

### 2.3 セグメントの重なりの問題

**現在の実装**:
```typescript:117:135:frontend/src/components/admin/CategoryChart.vue
const segments = computed(() => {
  let currentOffset = 0
  
  // 値が0より大きいカテゴリのみをフィルタ
  const validItems = chartData.value.filter((item) => item.value > 0)
  
  return validItems.map((item) => {
    const percentage = total.value > 0 ? item.value / total.value : 0
    const dashLength = circumference * percentage
    const offset = circumference - (currentOffset + dashLength)
    
    currentOffset += dashLength
    
    return {
      color: item.color,
      offset: offset
    }
  })
})
```

**問題**: `offset = circumference - (currentOffset + dashLength)`の計算が**逆順**になっている

**正しい計算方法**:
- 最初のセグメント: `offset = circumference - dashLength`
- 2番目のセグメント: `offset = circumference - (前のセグメントのoffset + 前のセグメントのdashLength)`
- しかし、現在の実装では`currentOffset`を累積しているが、`offset`の計算が間違っている

---

## 3. 根本原因の特定（可能性の高い順）

### 3.1 🔴 **最優先: `stroke-dashoffset`の計算ロジックが間違っている**

**原因**: `offset = circumference - (currentOffset + dashLength)`の計算式が間違っている

**問題の詳細**:
- SVGの`stroke-dashoffset`は、**円の開始位置からのオフセット**を指定する
- 現在の実装では、各セグメントが**重なって描画**されている
- 最後のセグメント（Trouble、赤色）が`offset=0`で、**全てのセグメントを覆っている**

**計算の流れ**:
1. **Basic (青色)**: `offset = 502.65 - (0 + 62.83) = 439.82` → 円の439.82pxの位置から62.83px描画
2. **Facilities (緑色)**: `offset = 502.65 - (62.83 + 376.99) = 62.83` → 円の62.83pxの位置から376.99px描画
3. **Location (黄色)**: `offset = 502.65 - (439.82 + 31.42) = 31.42` → 円の31.42pxの位置から31.42px描画
4. **Trouble (赤色)**: `offset = 502.65 - (471.24 + 31.42) = 0` → 円の0pxの位置から31.42px描画

**問題**: セグメントが**重なって描画**されており、最後のセグメント（Trouble、赤色）が全てを覆っている

**正しい計算方法**:
```typescript
const segments = computed(() => {
  let currentOffset = 0
  
  const validItems = chartData.value.filter((item) => item.value > 0)
  
  return validItems.map((item) => {
    const percentage = total.value > 0 ? item.value / total.value : 0
    const dashLength = circumference * percentage
    const offset = currentOffset  // 現在のオフセット位置から開始
    
    currentOffset += dashLength  // 次のセグメントの開始位置を更新
    
    return {
      color: item.color,
      offset: offset  // 正しいオフセット
    }
  })
})
```

### 3.2 ⚠️ **中優先度: SVGの`transform -rotate-90`による回転の問題**

**原因**: SVGが`-90度`回転しているため、セグメントの開始位置がずれている可能性

**問題の詳細**:
- SVGが`transform -rotate-90`で回転している
- これにより、セグメントの開始位置が**12時の位置から9時の位置**に移動している
- `stroke-dashoffset`の計算が、回転を考慮していない可能性がある

**影響**: セグメントの位置がずれる可能性があるが、色が全て赤色になる直接の原因ではない

### 3.3 ⚠️ **中優先度: セグメントの描画順序の問題**

**原因**: セグメントが**後から描画される順序**で、最後のセグメントが全てを覆っている

**問題の詳細**:
- SVGでは、**後から描画された要素が前面に表示**される
- 現在の実装では、`validItems`の順序（Basic → Facilities → Location → Trouble）で描画されている
- 最後のセグメント（Trouble、赤色）が`offset=0`で、**全てのセグメントを覆っている**

**影響**: セグメントが重なって描画され、最後のセグメントが全てを覆っている

### 3.4 ⚠️ **低優先度: `stroke-dasharray`の値が全て同じ**

**原因**: 全てのセグメントで`stroke-dasharray="502.6548245743669"`（circumference）が設定されている

**問題の詳細**:
- `stroke-dasharray`は、**破線のパターン**を指定する
- 円グラフでは、`stroke-dasharray`を`circumference`に設定し、`stroke-dashoffset`で位置を調整する
- 現在の実装では、全てのセグメントで`stroke-dasharray="circumference"`が設定されている

**影響**: これは正しい実装だが、`stroke-dashoffset`の計算が間違っているため、セグメントが重なっている

---

## 4. 根本原因の確定

### 4.1 確定した根本原因

🔴 **`stroke-dashoffset`の計算ロジックが間違っている**

**現在の実装**:
```typescript
const offset = circumference - (currentOffset + dashLength)
```

**問題点**:
1. `offset`の計算が**逆順**になっている
2. セグメントが**重なって描画**されている
3. 最後のセグメント（Trouble、赤色）が`offset=0`で、**全てのセグメントを覆っている**

**正しい実装**:
```typescript
const offset = currentOffset  // 現在のオフセット位置から開始
currentOffset += dashLength  // 次のセグメントの開始位置を更新
```

### 4.2 計算の検証

**現在の実装での計算**:
- Basic: `offset = 502.65 - (0 + 62.83) = 439.82`
- Facilities: `offset = 502.65 - (62.83 + 376.99) = 62.83`
- Location: `offset = 502.65 - (439.82 + 31.42) = 31.42`
- Trouble: `offset = 502.65 - (471.24 + 31.42) = 0`

**問題**: セグメントが重なって描画されており、最後のセグメント（Trouble、赤色）が全てを覆っている

**正しい実装での計算**:
- Basic: `offset = 0`, `dashLength = 62.83` → 0pxから62.83px描画
- Facilities: `offset = 62.83`, `dashLength = 376.99` → 62.83pxから439.82px描画
- Location: `offset = 439.82`, `dashLength = 31.42` → 439.82pxから471.24px描画
- Trouble: `offset = 471.24`, `dashLength = 31.42` → 471.24pxから502.65px描画

**結果**: セグメントが**連続して描画**され、重ならない

---

## 5. 修正方法

### 5.1 修正内容

**ファイル**: `frontend/src/components/admin/CategoryChart.vue`

**修正前**:
```typescript:117:135:frontend/src/components/admin/CategoryChart.vue
const segments = computed(() => {
  let currentOffset = 0
  
  // 値が0より大きいカテゴリのみをフィルタ
  const validItems = chartData.value.filter((item) => item.value > 0)
  
  return validItems.map((item) => {
    const percentage = total.value > 0 ? item.value / total.value : 0
    const dashLength = circumference * percentage
    const offset = circumference - (currentOffset + dashLength)  // ← 間違った計算
    
    currentOffset += dashLength
    
    return {
      color: item.color,
      offset: offset
    }
  })
})
```

**修正後**:
```typescript
const segments = computed(() => {
  let currentOffset = 0
  
  // 値が0より大きいカテゴリのみをフィルタ
  const validItems = chartData.value.filter((item) => item.value > 0)
  
  return validItems.map((item) => {
    const percentage = total.value > 0 ? item.value / total.value : 0
    const dashLength = circumference * percentage
    const offset = currentOffset  // ← 正しい計算: 現在のオフセット位置から開始
    
    currentOffset += dashLength  // 次のセグメントの開始位置を更新
    
    return {
      color: item.color,
      offset: offset
    }
  })
})
```

### 5.2 修正の効果

**修正前**:
- セグメントが重なって描画される
- 最後のセグメント（Trouble、赤色）が全てを覆う
- グラフが全て赤色で表示される

**修正後**:
- セグメントが連続して描画される
- 各セグメントが正しい色で表示される
- グラフが正しく色分けされる

---

## 6. まとめ

### 6.1 根本原因

🔴 **`stroke-dashoffset`の計算ロジックが間違っている**

**問題点**:
- `offset = circumference - (currentOffset + dashLength)`の計算式が間違っている
- セグメントが重なって描画されている
- 最後のセグメント（Trouble、赤色）が全てを覆っている

### 6.2 修正方法

**修正内容**:
- `offset = currentOffset`に変更（現在のオフセット位置から開始）
- `currentOffset += dashLength`で次のセグメントの開始位置を更新

### 6.3 修正の優先度

🔴 **最優先**: 根本原因が特定できたため、修正を実施すべき

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-04  
**Status**: 🔴 **根本原因特定完了、修正待ち**


