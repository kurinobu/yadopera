/**
 * ゲスト画面：スタッフ返信の取得・表示まわりの文言
 */

export interface StaffReplyGuestStrings {
  /** 自動更新の案内 */
  noticeAutoUpdate: string
  /** 手動更新の案内 */
  noticeManualRefresh: string
  refreshButton: string
  refreshing: string
  staffLabel: string
}

const STR_JA: StaffReplyGuestStrings = {
  noticeAutoUpdate: 'スタッフからのお返事があれば、自動で表示されます（最大10分）。',
  noticeManualRefresh: '表示されないときは「更新」を押してください。',
  refreshButton: '更新',
  refreshing: '更新中…',
  staffLabel: 'スタッフ'
}

const STR_EN: StaffReplyGuestStrings = {
  noticeAutoUpdate: 'If staff reply, it will appear here automatically (up to 10 minutes).',
  noticeManualRefresh: 'If you do not see a reply, tap Refresh.',
  refreshButton: 'Refresh',
  refreshing: 'Refreshing…',
  staffLabel: 'Staff'
}

const MAP: Record<string, StaffReplyGuestStrings> = {
  ja: STR_JA,
  en: STR_EN
}

export function getStaffReplyGuestCopy(lang: string): StaffReplyGuestStrings {
  const key = (lang || '').trim() || 'en'
  return MAP[key] ?? STR_EN
}
