/**
 * 開発時のみ console 出力するロガー（本番では無効）
 * ゲストチャット表示遅延報告書 10.2.1 に基づく。
 */

const isDev = import.meta.env.DEV

export const log = isDev
  ? (...args: unknown[]) => console.log(...args)
  : () => {}

export const warn = isDev
  ? (...args: unknown[]) => console.warn(...args)
  : () => {}
