/**
 * FAQ管理API（インテントベース構造対応）
 * 
 * 注意: FAQはインテント単位でカウントされます。
 * 複数言語対応しても1件としてカウントされます。
 */

import apiClient from './axios'
import type { FAQ, FAQCreate, FAQUpdate } from '@/types/faq'

/** CSV一括アップロード結果 */
export interface BulkUploadResult {
  success_count: number
  failure_count: number
  total_count: number
  skipped_count: number
  processing_time_seconds: number
  uploaded_at: string
  uploaded_by: number
  errors: Array<Record<string, unknown>>
  warnings: Array<Record<string, unknown>>
}

export const faqApi = {
  /**
   * FAQ一覧取得（インテントベース構造）
   * 
   * @param category - カテゴリフィルタ（オプション）
   * @param isActive - 有効/無効フィルタ（オプション）
   * @returns FAQリスト（translationsを含む）と進行中フラグ
   * 
   * 注意: 返されるFAQはインテント単位で、translationsに複数言語の翻訳が含まれます。
   */
  async getFaqs(category?: string, isActive?: boolean): Promise<{ faqs: FAQ[]; total: number; is_initializing: boolean }> {
    const params: Record<string, any> = {}
    if (category) params.category = category
    if (isActive !== undefined) params.is_active = isActive
    
    const response = await apiClient.get<{ faqs: FAQ[]; total: number; is_initializing: boolean }>('/admin/faqs', { params })
    // totalはインテント単位でカウント（言語に関係なく、FAQ.idをカウント）
    return response.data
  },

  /**
   * FAQ作成（インテントベース構造）
   * 
   * @param data - FAQ作成データ（translationsリストを含む）
   * @returns 作成されたFAQ（translationsを含む）
   * 
   * 注意: translationsに最低1つの言語が必要です。
   * intent_keyが指定されていない場合は自動生成されます。
   */
  async createFaq(data: FAQCreate): Promise<FAQ> {
    const response = await apiClient.post<FAQ>('/admin/faqs', data)
    return response.data
  },

  /**
   * FAQ更新（インテントベース構造）
   * 
   * @param faqId - FAQ ID
   * @param data - FAQ更新データ（translationsリストを含む、オプション）
   * @returns 更新されたFAQ（translationsを含む）
   * 
   * 注意: translationsが指定された場合、既存の翻訳が更新または新規作成されます。
   */
  async updateFaq(faqId: number, data: FAQUpdate): Promise<FAQ> {
    const response = await apiClient.put<FAQ>(`/admin/faqs/${faqId}`, data)
    return response.data
  },

  /**
   * FAQ削除
   * 
   * @param faqId - FAQ ID
   * 
   * 注意: FAQを削除すると、関連するすべての翻訳（FAQTranslation）も削除されます。
   */
  async deleteFaq(faqId: number): Promise<void> {
    await apiClient.delete(`/admin/faqs/${faqId}`)
  },

  /**
   * CSV一括アップロード（Standard/Premiumプランのみ）
   * @param file - CSVファイル
   * @param mode - 登録モード（add: 追加のみ）
   * @param onProgress - 送信進捗コールバック（0-100）
   */
  async bulkUploadCsv(
    file: File,
    mode: string = 'add',
    onProgress?: (percent: number) => void
  ): Promise<BulkUploadResult> {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('mode', mode)
    const response = await apiClient.post<BulkUploadResult>('/admin/faqs/bulk-upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (e) => {
        if (onProgress && e.total != null && e.total > 0) {
          onProgress(Math.round((e.loaded / e.total) * 100))
        }
      }
    })
    return response.data
  }
}


