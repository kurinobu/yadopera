<template>
  <div class="space-y-6">
    <!-- ページヘッダー -->
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">
        施設設定
      </h1>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">
        施設情報の編集と各種設定
      </p>
    </div>

    <!-- ローディング表示 -->
    <Loading v-if="isLoading" />

    <!-- エラー表示 -->
    <div
      v-else-if="error"
      class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4"
    >
      <p class="text-red-800 dark:text-red-200">{{ error }}</p>
      <button
        @click="fetchSettings"
        class="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
      >
        再試行
      </button>
    </div>

    <!-- メインコンテンツ -->
    <div v-else class="space-y-6">
      <!-- 基本情報セクション -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          基本情報
        </h2>
        <div class="space-y-4">
          <Input
            v-model="formData.name"
            type="text"
            label="施設名"
            placeholder="例: YadOPERAゲストハウス"
            :required="true"
            :maxlength="255"
            :error="errors.name"
          />
          <Input
            v-model="formData.email"
            type="email"
            label="メールアドレス"
            placeholder="例: info@example.com"
            :required="true"
            :maxlength="255"
            :error="errors.email"
          />
          <div class="flex items-center space-x-2">
            <input
              id="show_email_on_guest_screen"
              v-model="formData.show_email_on_guest_screen"
              type="checkbox"
              class="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
            />
            <label for="show_email_on_guest_screen" class="text-sm text-gray-700 dark:text-gray-300">
              ゲスト画面にメールアドレスを表示する
            </label>
          </div>
          <p v-if="formData.show_email_on_guest_screen" class="text-xs text-amber-600 dark:text-amber-400">
            このメールアドレスはゲスト画面に表示されます。ログイン用のメールアドレスとは別の、施設用・問い合わせ用のメールアドレスを設定してください。
          </p>
          <Input
            v-model="formData.phone"
            type="tel"
            label="電話番号"
            placeholder="例: 090-1234-5678"
            :maxlength="50"
            :error="errors.phone"
          />
          <p class="text-xs text-gray-600 dark:text-gray-400">
            この電話番号は入力して保存するとゲスト画面に表示されます。
          </p>
          <Input
            v-model="formData.address"
            type="textarea"
            label="住所"
            placeholder="例: 京都府京都市..."
            :rows="2"
            :error="errors.address"
          />
        </div>
      </div>

      <!-- WiFi設定セクション -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          WiFi設定
        </h2>
        <div class="space-y-4">
          <Input
            v-model="formData.wifi_ssid"
            type="text"
            label="WiFi SSID"
            placeholder="例: Yadopera-Guest"
            :maxlength="100"
            :error="errors.wifi_ssid"
          />
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              WiFiパスワード
            </label>
            <div class="flex items-center space-x-2">
              <div class="flex-1">
                <Input
                  v-model="formData.wifi_password"
                  :type="showWifiPassword ? 'text' : 'password'"
                  placeholder="変更する場合のみ入力"
                  :maxlength="100"
                  :error="errors.wifi_password"
                />
              </div>
              <button
                type="button"
                @click="showWifiPassword = !showWifiPassword"
                class="px-3 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
              >
                {{ showWifiPassword ? '非表示' : '表示' }}
              </button>
            </div>
            <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
              変更する場合のみ入力してください。現在のパスワードは表示されません。
            </p>
          </div>
        </div>
      </div>

      <!-- チェックイン/アウト時間セクション -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          チェックイン/アウト時間
        </h2>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              チェックイン時間
            </label>
            <input
              v-model="formData.check_in_time"
              type="time"
              class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p v-if="errors.check_in_time" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ errors.check_in_time }}
            </p>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              チェックアウト時間
            </label>
            <input
              v-model="formData.check_out_time"
              type="time"
              class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <p v-if="errors.check_out_time" class="mt-1 text-sm text-red-600 dark:text-red-400">
              {{ errors.check_out_time }}
            </p>
          </div>
        </div>
      </div>

      <!-- 館内ルール・周辺情報・禁止事項セクション -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          館内ルール・周辺情報・禁止事項
        </h2>
        <div class="space-y-4">
          <Input
            v-model="formData.house_rules"
            type="textarea"
            label="館内ルール"
            placeholder="例: 門限23:00、静粛時間22:00-8:00"
            :rows="4"
            :maxlength="500"
            hint="500文字以内（AI応答のコンテキストに使用されます）"
            :error="errors.house_rules"
          />
          <Input
            v-model="formData.local_info"
            type="textarea"
            label="周辺情報"
            placeholder="例: 最寄り駅: 京都駅（徒歩10分）、コンビニ: セブンイレブン（徒歩3分）、レストラン: 多数あり"
            :rows="4"
            :maxlength="500"
            hint="500文字以内（AI応答のコンテキストに使用されます）"
            :error="errors.local_info"
          />
          <Input
            v-model="formData.prohibited_items"
            type="textarea"
            label="禁止事項"
            placeholder="例: 喫煙、大声、飲酒、ペットの持ち込み"
            :rows="4"
            :maxlength="500"
            hint="500文字以内（AI応答のコンテキストに使用されます）"
            :error="errors.prohibited_items"
          />
        </div>
      </div>

      <!-- クーポン（リードゲット）設定セクション -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          クーポン設定（リード獲得）
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          ゲストに「オトクなクーポン」を案内し、メールアドレスを取得できます。次回の公式サイト予約で割引としてご利用いただけます。
        </p>
        <div class="space-y-4">
          <div class="flex items-center gap-3">
            <input
              id="coupon-enabled"
              v-model="formData.coupon_enabled"
              type="checkbox"
              class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
            />
            <label for="coupon-enabled" class="text-sm font-medium text-gray-700 dark:text-gray-300">
              クーポンを有効にする
            </label>
          </div>
          <template v-if="formData.coupon_enabled">
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                割引率（%）
              </label>
              <input
                v-model.number="formData.coupon_discount_percent"
                type="number"
                min="1"
                max="100"
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 max-w-[120px]"
              />
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">5〜20%程度を推奨</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                クーポン文言（任意）
              </label>
              <input
                v-model="formData.coupon_description"
                type="text"
                maxlength="500"
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="例: 次回ご予約時にご提示ください"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                有効期限（発行日から何ヶ月）
              </label>
              <input
                v-model.number="formData.coupon_validity_months"
                type="number"
                min="1"
                max="24"
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500 max-w-[120px]"
              />
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">例: 6 で6ヶ月</p>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                公式サイトURL（任意）
              </label>
              <input
                v-model="formData.official_website_url"
                type="url"
                maxlength="500"
                class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="https://example.com"
              />
              <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">クーポン送付メールに「ご予約はこちら」のリンクとして表示されます</p>
            </div>
          </template>
        </div>
      </div>

      <!-- 対応言語セクション（表示のみ） -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          対応言語
        </h2>
        <div class="space-y-2">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ settings?.facility.languages.join(', ') || 'en' }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            現在は英語のみ対応。多言語対応はPhase 2以降で実装予定です。
          </p>
        </div>
      </div>

      <!-- タイムゾーンセクション（表示のみ） -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          タイムゾーン
        </h2>
        <div class="space-y-2">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ settings?.facility.timezone || 'Asia/Tokyo' }}
          </p>
          <p class="text-xs text-gray-500 dark:text-gray-400">
            現在は日本国内のみ対応のため、タイムゾーンは固定です。
          </p>
        </div>
      </div>

      <!-- スタッフ不在時間帯セクション -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          スタッフ不在時間帯
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          スタッフが不在の時間帯を設定します。この時間帯にエスカレーションが発生した場合、スタッフ不在時間帯対応キューに追加されます。
        </p>
        <div class="space-y-4">
          <div
            v-for="(period, index) in formData.staff_absence_periods"
            :key="index"
            class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-4"
          >
            <div class="flex items-center justify-between">
              <h3 class="text-sm font-medium text-gray-900 dark:text-white">
                時間帯 {{ index + 1 }}
              </h3>
              <button
                type="button"
                @click="removeAbsencePeriod(index)"
                class="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300 text-sm"
              >
                削除
              </button>
            </div>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  開始時刻
                </label>
                <input
                  v-model="period.start_time"
                  type="time"
                  class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  終了時刻
                </label>
                <input
                  v-model="period.end_time"
                  type="time"
                  class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                曜日
              </label>
              <div class="flex flex-wrap gap-2">
                <label
                  v-for="day in daysOfWeek"
                  :key="day.value"
                  class="flex items-center space-x-2 cursor-pointer"
                >
                  <input
                    v-model="period.days_of_week"
                    type="checkbox"
                    :value="day.value"
                    class="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300">{{ day.label }}</span>
                </label>
              </div>
            </div>
          </div>
          <button
            type="button"
            @click="addAbsencePeriod"
            class="w-full px-4 py-2 text-sm font-medium text-blue-600 dark:text-blue-400 border border-blue-600 dark:border-blue-400 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
          >
            + 時間帯を追加
          </button>
        </div>
      </div>

      <!-- パスワード変更セクション -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          パスワード変更
        </h2>
        <div class="space-y-4">
          <Input
            v-model="passwordForm.current_password"
            type="password"
            label="現在のパスワード"
            placeholder="現在のパスワードを入力"
            :required="true"
            :error="passwordErrors.current_password"
          />
          <Input
            v-model="passwordForm.new_password"
            type="password"
            label="新しいパスワード"
            placeholder="新しいパスワードを入力（最小8文字）"
            :required="true"
            :minlength="8"
            :error="passwordErrors.new_password"
          />
          <Input
            v-model="passwordForm.confirm_password"
            type="password"
            label="新しいパスワード（確認）"
            placeholder="新しいパスワードを再入力"
            :required="true"
            :minlength="8"
            :error="passwordErrors.confirm_password"
          />
          <button
            type="button"
            @click="handlePasswordChange"
            :disabled="isChangingPassword || !isPasswordFormValid"
            class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {{ isChangingPassword ? '変更中...' : 'パスワードを変更' }}
          </button>
        </div>
      </div>

      <!-- アイコン設定セクション（任意、Phase 1では簡略化） -->
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          アイコン設定
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Phase 2以降で実装予定です。
        </p>
      </div>

      <!-- 保存ボタン -->
      <div class="flex items-center justify-end space-x-3 pt-4">
        <button
          type="button"
          @click="handleCancel"
          class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
        >
          キャンセル
        </button>
        <button
          type="button"
          @click="handleSave"
          :disabled="isSaving"
          class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ isSaving ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import Input from '@/components/common/Input.vue'
import Loading from '@/components/common/Loading.vue'
import { facilityApi } from '@/api/facility'
import { authApi } from '@/api/auth'
import type {
  FacilitySettingsResponse,
  FacilitySettingsUpdateRequest,
  PasswordChangeRequest
} from '@/types/facility'
import type { StaffAbsencePeriod } from '@/types/facility'

const router = useRouter()

// データ状態
const isLoading = ref(false)
const isSaving = ref(false)
const isChangingPassword = ref(false)
const error = ref<string | null>(null)
const settings = ref<FacilitySettingsResponse | null>(null)
const showWifiPassword = ref(false)
/** ログインユーザーのメール（同一メール禁止チェック用） */
const currentUserEmail = ref<string>('')

// フォームデータ
const formData = ref<{
  name: string
  email: string
  phone: string
  address: string
  wifi_ssid: string
  wifi_password: string
  check_in_time: string
  check_out_time: string
  house_rules: string
  local_info: string
  prohibited_items: string
  staff_absence_periods: StaffAbsencePeriod[]
  coupon_enabled: boolean
  coupon_discount_percent: number | null
  coupon_description: string
  coupon_validity_months: number | null
  official_website_url: string
  show_email_on_guest_screen: boolean
}>({
  name: '',
  email: '',
  phone: '',
  address: '',
  wifi_ssid: '',
  wifi_password: '',
  check_in_time: '',
  check_out_time: '',
  house_rules: '',
  local_info: '',
  prohibited_items: '',
  staff_absence_periods: [],
  coupon_enabled: false,
  coupon_discount_percent: null,
  coupon_description: '',
  coupon_validity_months: 6,
  official_website_url: '',
  show_email_on_guest_screen: true
})

// パスワード変更フォーム
const passwordForm = ref<PasswordChangeRequest>({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

// バリデーションエラー
const errors = ref<Record<string, string>>({})
const passwordErrors = ref<Record<string, string>>({})

// 曜日オプション
const daysOfWeek = [
  { value: 'mon', label: '月' },
  { value: 'tue', label: '火' },
  { value: 'wed', label: '水' },
  { value: 'thu', label: '木' },
  { value: 'fri', label: '金' },
  { value: 'sat', label: '土' },
  { value: 'sun', label: '日' }
]

// パスワードフォームのバリデーション
const isPasswordFormValid = computed(() => {
  return (
    passwordForm.value.current_password.length > 0 &&
    passwordForm.value.new_password.length >= 8 &&
    passwordForm.value.confirm_password.length >= 8 &&
    passwordForm.value.new_password === passwordForm.value.confirm_password
  )
})

// 施設設定を取得
const fetchSettings = async () => {
  try {
    isLoading.value = true
    error.value = null
    
    const response = await facilityApi.getFacilitySettings()
    settings.value = response
    
    // フォームデータに設定
    // 時刻形式を変換（"15:00" → "15:00"、HTML time input用）
    const formatTimeForInput = (timeStr: string | undefined): string => {
      if (!timeStr) return ''
      // "15:00"形式の場合はそのまま返す
      if (timeStr.match(/^\d{2}:\d{2}$/)) {
        return timeStr
      }
      return ''
    }
    
    formData.value = {
      name: response.facility.name,
      email: response.facility.email,
      phone: response.facility.phone || '',
      address: response.facility.address || '',
      wifi_ssid: response.facility.wifi_ssid || '',
      wifi_password: '',  // パスワードは表示しない
      check_in_time: formatTimeForInput(response.facility.check_in_time),
      check_out_time: formatTimeForInput(response.facility.check_out_time),
      house_rules: response.facility.house_rules || '',
      local_info: response.facility.local_info || '',
      prohibited_items: response.facility.prohibited_items || '',
      staff_absence_periods: response.staff_absence_periods.length > 0
        ? response.staff_absence_periods.map(period => ({
            start_time: period.start_time,
            end_time: period.end_time,
            days_of_week: [...period.days_of_week]
          }))
        : [{ start_time: '22:00', end_time: '08:00', days_of_week: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun'] }],
      coupon_enabled: response.facility.coupon_enabled ?? false,
      coupon_discount_percent: response.facility.coupon_discount_percent ?? null,
      coupon_description: response.facility.coupon_description ?? '',
      coupon_validity_months: response.facility.coupon_validity_months ?? 6,
      official_website_url: response.facility.official_website_url ?? '',
      show_email_on_guest_screen: response.facility.show_email_on_guest_screen ?? true
    }
    // ログインユーザーのメールを取得（同一メール禁止チェック用）
    try {
      const user = await authApi.getCurrentUser()
      currentUserEmail.value = user.email ?? ''
    } catch {
      currentUserEmail.value = ''
    }
  } catch (err: any) {
    error.value = '施設設定の取得に失敗しました'
    console.error('Facility settings fetch error:', err)
  } finally {
    isLoading.value = false
  }
}

// スタッフ不在時間帯を追加
const addAbsencePeriod = () => {
  formData.value.staff_absence_periods = formData.value.staff_absence_periods || []
  formData.value.staff_absence_periods.push({
    start_time: '22:00',
    end_time: '08:00',
    days_of_week: ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
  })
}

// スタッフ不在時間帯を削除
const removeAbsencePeriod = (index: number) => {
  if (formData.value.staff_absence_periods) {
    formData.value.staff_absence_periods.splice(index, 1)
  }
}

// 保存処理
const handleSave = async () => {
  try {
    isSaving.value = true
    errors.value = {}
    
    // バリデーション
    if (!formData.value.name || formData.value.name.trim().length === 0) {
      errors.value.name = '施設名は必須です'
      return
    }
    if (!formData.value.email || formData.value.email.trim().length === 0) {
      errors.value.email = 'メールアドレスは必須です'
      return
    }
    // ゲストに表示するが ON のとき、施設メールがログインメールと同一ならエラー
    if (formData.value.show_email_on_guest_screen && currentUserEmail.value) {
      const facilityEmail = formData.value.email.trim().toLowerCase()
      const loginEmail = currentUserEmail.value.trim().toLowerCase()
      if (facilityEmail === loginEmail) {
        errors.value.email = '施設の連絡先メールは、ログインに使用しているメールアドレスとは別のものを設定してください。'
        return
      }
    }
    
    // WiFiパスワードが空の場合は送信しない
    const updateData: FacilitySettingsUpdateRequest = { ...formData.value }
    if (!updateData.wifi_password || updateData.wifi_password.trim().length === 0) {
      delete updateData.wifi_password
    }

    await facilityApi.updateFacilitySettings(updateData)
    
    // 成功メッセージ
    alert('施設設定を保存しました')
    
    // 再取得
    await fetchSettings()
  } catch (err: any) {
    console.error('Failed to save facility settings:', err)
    const detail = err.response?.data?.detail || err.message || ''
    alert(`保存に失敗しました: ${detail}`)
  } finally {
    isSaving.value = false
  }
}

// パスワード変更処理
const handlePasswordChange = async () => {
  try {
    isChangingPassword.value = true
    passwordErrors.value = {}
    
    // バリデーション
    if (!passwordForm.value.current_password) {
      passwordErrors.value.current_password = '現在のパスワードは必須です'
      return
    }
    if (passwordForm.value.new_password.length < 8) {
      passwordErrors.value.new_password = '新しいパスワードは8文字以上である必要があります'
      return
    }
    if (passwordForm.value.new_password !== passwordForm.value.confirm_password) {
      passwordErrors.value.confirm_password = '新しいパスワードと確認パスワードが一致しません'
      return
    }
    
    await authApi.changePassword(passwordForm.value)
    
    // 成功メッセージ
    alert('パスワードを変更しました')
    
    // フォームをクリア
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (err: any) {
    console.error('Failed to change password:', err)
    const detail = err.response?.data?.detail || err.message || ''
    let errorMessage = 'パスワードの変更に失敗しました'
    
    if (detail.includes('Current password is incorrect')) {
      errorMessage = '現在のパスワードが正しくありません'
      passwordErrors.value.current_password = '現在のパスワードが正しくありません'
    } else if (detail.includes('do not match')) {
      errorMessage = '新しいパスワードと確認パスワードが一致しません'
      passwordErrors.value.confirm_password = '新しいパスワードと確認パスワードが一致しません'
    } else if (detail.includes('at least 8 characters')) {
      errorMessage = '新しいパスワードは8文字以上である必要があります'
      passwordErrors.value.new_password = '新しいパスワードは8文字以上である必要があります'
    } else if (detail) {
      errorMessage = `パスワードの変更に失敗しました: ${detail}`
    }
    
    alert(errorMessage)
  } finally {
    isChangingPassword.value = false
  }
}

// キャンセル処理
const handleCancel = () => {
  router.push('/admin/dashboard')
}

// 初期化（fetchSettings 内で getCurrentUser も呼ぶ）
onMounted(() => {
  fetchSettings()
})
</script>

<style scoped>
/* Component styles */
</style>

