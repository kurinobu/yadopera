# Phase 1: QRCodeGenerator.vue 構文エラー 調査分析・修正案

**作成日時**: 2025年12月6日 12:00  
**最終更新日時**: 2025年12月6日 12:00  
**実施者**: Auto (AI Assistant)  
**対象**: `frontend/src/views/admin/QRCodeGenerator.vue`の構文エラー  
**状態**: ✅ **調査分析完了、修正案提示完了**  
**ファイル名**: `Phase1_QRCodeGenerator_構文エラー_調査分析_修正案_20251206_1200.md`

---

## 1. エラー内容

### 1.1 エラーメッセージ

```
[plugin:vite:vue] [vue/compiler-sfc] Unexpected token (167:0)

/app/src/views/admin/QRCodeGenerator.vue:167:0

290|    if (index !== -1) {
291|      generatedQRCodes.value.splice(index, 1)
292|    }
293|
/app/src/views/admin/QRCodeGenerator.vue:167:0
```

### 1.2 エラーの発生箇所

- **ファイル**: `frontend/src/views/admin/QRCodeGenerator.vue`
- **行番号**: 289-293行目
- **エラー種別**: 構文エラー（重複コード）

---

## 2. 原因の調査

### 2.1 問題の特定

**289-293行目に重複したコードが存在**:

```typescript
const handleRemoveFromList = async (id: number) => {
  try {
    await qrcodeApi.deleteQRCode(id)
    // 一覧から削除
    const index = generatedQRCodes.value.findIndex(qr => qr.id === id)
    if (index !== -1) {
      generatedQRCodes.value.splice(index, 1)
    }
  } catch (err: any) {
    console.error('Failed to delete QR code:', err)
    alert(err.response?.data?.detail || 'QRコードの削除に失敗しました')
  }
}  // ← 288行目で関数が終了
  const index = generatedQRCodes.value.findIndex(qr => qr.id === id)  // ← 289行目: 重複コード
  if (index !== -1) {
    generatedQRCodes.value.splice(index, 1)
  }
}  // ← 293行目: 不要な閉じ括弧
```

### 2.2 原因の分析

**修正時のミス**:
- `handleRemoveFromList`関数を修正する際、古いコードを削除し忘れた
- 288行目の`}`で関数が終了しているのに、289-293行目に古いコードが残っている
- これにより、関数の外にコードが存在し、構文エラーが発生

**正しいコード構造**:
```typescript
const handleRemoveFromList = async (id: number) => {
  try {
    await qrcodeApi.deleteQRCode(id)
    // 一覧から削除
    const index = generatedQRCodes.value.findIndex(qr => qr.id === id)
    if (index !== -1) {
      generatedQRCodes.value.splice(index, 1)
    }
  } catch (err: any) {
    console.error('Failed to delete QR code:', err)
    alert(err.response?.data?.detail || 'QRコードの削除に失敗しました')
  }
}  // ← ここで関数終了
// ← 次の関数が続く
```

---

## 3. 修正案

### 3.1 修正案1: 重複コードの削除（推奨）

#### 修正内容

**289-293行目の重複コードを削除**:

```typescript
// 修正前（276-293行目）
const handleRemoveFromList = async (id: number) => {
  try {
    await qrcodeApi.deleteQRCode(id)
    // 一覧から削除
    const index = generatedQRCodes.value.findIndex(qr => qr.id === id)
    if (index !== -1) {
      generatedQRCodes.value.splice(index, 1)
    }
  } catch (err: any) {
    console.error('Failed to delete QR code:', err)
    alert(err.response?.data?.detail || 'QRコードの削除に失敗しました')
  }
}
  const index = generatedQRCodes.value.findIndex(qr => qr.id === id)  // ← 削除
  if (index !== -1) {  // ← 削除
    generatedQRCodes.value.splice(index, 1)  // ← 削除
  }
}  // ← 削除

// 修正後（276-288行目）
const handleRemoveFromList = async (id: number) => {
  try {
    await qrcodeApi.deleteQRCode(id)
    // 一覧から削除
    const index = generatedQRCodes.value.findIndex(qr => qr.id === id)
    if (index !== -1) {
      generatedQRCodes.value.splice(index, 1)
    }
  } catch (err: any) {
    console.error('Failed to delete QR code:', err)
    alert(err.response?.data?.detail || 'QRコードの削除に失敗しました')
  }
}
```

#### 修正箇所

**`frontend/src/views/admin/QRCodeGenerator.vue`**:
- **289-293行目を削除**

#### メリット

- 構文エラーが解消される
- コードが正しく動作する
- 重複コードがなくなり、保守性が向上する

---

## 4. 実装手順

### 4.1 修正手順

1. **`frontend/src/views/admin/QRCodeGenerator.vue`を開く**
2. **289-293行目を削除**
   - `  const index = generatedQRCodes.value.findIndex(qr => qr.id === id)`
   - `  if (index !== -1) {`
   - `    generatedQRCodes.value.splice(index, 1)`
   - `  }`
   - `}`
3. **ファイルを保存**
4. **ブラウザで動作確認**

### 4.2 確認事項

- 構文エラーが解消されているか
- `handleRemoveFromList`関数が正しく動作するか
- 「一覧から削除」ボタンが正常に動作するか

---

## 5. まとめ

### 5.1 問題の原因

**重複コードの存在**:
- `handleRemoveFromList`関数の修正時に、古いコードを削除し忘れた
- 289-293行目に重複したコードが残っている
- これにより、関数の外にコードが存在し、構文エラーが発生

### 5.2 修正案

**修正案1: 重複コードの削除（推奨）**

**修正内容**:
- 289-293行目の重複コードを削除

**メリット**:
- 構文エラーが解消される
- コードが正しく動作する
- 重複コードがなくなり、保守性が向上する

---

**Document Version**: v1.0  
**Author**: Auto (AI Assistant)  
**Last Updated**: 2025-12-06 12:00  
**Status**: ✅ **調査分析完了、修正案提示完了**


