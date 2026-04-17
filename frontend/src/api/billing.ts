/**
 * プラン・請求 API（Phase 4 Phase C 管理 API）
 * GET /admin/plans, POST /admin/plans/change, POST /admin/subscription/cancel,
 * GET /admin/invoices, GET /admin/invoices/:id/receipt
 */

import apiClient from './axios'

export interface PlanInfo {
  plan_type: string
  name_ja: string
  price_yen: number
  monthly_question_limit: number | null
  faq_limit: number | null
  language_limit: number | null
  language_codes: string[]
  language_names_ja: string[]
}

export interface PlansResponse {
  current_plan_type: string
  plans: PlanInfo[]
  stripe_configured: boolean
  /** 現在のプラン超過時挙動（continue_billing | faq_only） */
  current_overage_behavior?: string | null
}

export interface PlanChangeResponse {
  plan_type: string
  message: string
}

export interface SubscriptionCancelResponse {
  message: string
}

export interface InvoiceItem {
  id: string
  /** ISO 4217 lowercase（API は Stripe Invoice に合わせる。例: jpy, usd） */
  currency: string
  amount_due: number
  status: string | null
  created: number | null
  hosted_invoice_url: string | null
}

export interface InvoicesResponse {
  invoices: InvoiceItem[]
}

export interface ReceiptResponse {
  url: string
}

export const billingApi = {
  /** 現在プラン・変更可能プラン一覧 */
  async getPlans(): Promise<PlansResponse> {
    const res = await apiClient.get<PlansResponse>('/admin/plans')
    return res.data
  },

  /** プラン変更 */
  async changePlan(target_plan_type: string): Promise<PlanChangeResponse> {
    const res = await apiClient.post<PlanChangeResponse>('/admin/plans/change', {
      target_plan_type
    })
    return res.data
  },

  /** 解約（期間末 or 即時） */
  async cancelSubscription(at_period_end: boolean): Promise<SubscriptionCancelResponse> {
    const res = await apiClient.post<SubscriptionCancelResponse>('/admin/subscription/cancel', {
      at_period_end
    })
    return res.data
  },

  /** 請求履歴一覧 */
  async getInvoices(): Promise<InvoicesResponse> {
    const res = await apiClient.get<InvoicesResponse>('/admin/invoices')
    return res.data
  },

  /** 領収書 URL 取得（別タブで開く用） */
  async getReceiptUrl(invoice_id: string): Promise<ReceiptResponse> {
    const res = await apiClient.get<ReceiptResponse>(`/admin/invoices/${invoice_id}/receipt`)
    return res.data
  }
}
