<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <!-- 翻訳リスト（インテントベース構造対応） -->
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
        翻訳 <span class="text-red-500">*</span>
        <span class="text-xs text-gray-500 dark:text-gray-400 ml-2">
          （最低1つの言語が必要です）
        </span>
      </label>
      <div
        v-for="(translation, index) in formData.translations"
        :key="index"
        class="mb-4 p-4 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-800"
      >
        <div class="flex items-center justify-between mb-2">
          <label class="text-sm font-medium text-gray-700 dark:text-gray-300">
            言語 {{ index + 1 }}
          </label>
          <button
            v-if="formData.translations.length > 1"
            type="button"
            @click="removeTranslation(index)"
            class="text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
          >
            削除
          </button>
        </div>
        
        <div class="mb-3">
          <label class="block text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">
            言語
          </label>
          <select
            v-model="translation.language"
            class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option
              v-for="opt in languageRowOptions(index)"
              :key="opt.code"
              :value="opt.code"
              :disabled="opt.disabled"
            >
              {{ opt.label }}{{ opt.disabledReason ? ` — ${opt.disabledReason}` : '' }}
            </option>
          </select>
        </div>

        <Input
          v-model="translation.question"
          type="textarea"
          :label="`質問文 (${translation.language})`"
          :placeholder="`例: What is the WiFi password?`"
          :required="true"
          :maxlength="500"
          :rows="3"
          hint="500文字以内"
          :error="errors[`translation_${index}_question`]"
          @blur="() => validateTranslationQuestion(index)"
        />

        <Input
          v-model="translation.answer"
          type="textarea"
          :label="`回答文 (${translation.language})`"
          :placeholder="`例: The WiFi password is guest2024.`"
          :required="true"
          :maxlength="2000"
          :rows="4"
          hint="2000文字以内"
          :error="errors[`translation_${index}_answer`]"
          @blur="() => validateTranslationAnswer(index)"
        />
      </div>
      
      <button
        type="button"
        @click="addTranslation"
        class="text-sm text-blue-600 hover:text-blue-700 dark:text-blue-400 dark:hover:text-blue-300"
      >
        + 翻訳を追加
      </button>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        カテゴリ <span class="text-red-500">*</span>
      </label>
      <select
        v-model="formData.category"
        :class="[
          'block w-full rounded-lg border shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-0 transition-colors',
          errors.category
            ? 'border-red-300 focus:border-red-500 focus:ring-red-500'
            : 'border-gray-300 focus:border-blue-500 focus:ring-blue-500 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-200',
          'px-3 py-2 text-sm'
        ]"
        required
      >
        <option value="">選択してください</option>
        <option value="basic">Basic</option>
        <option value="facilities">Facilities</option>
        <option value="location">Location</option>
        <option value="trouble">Trouble</option>
      </select>
      <p v-if="errors.category" class="mt-1 text-sm text-red-600 dark:text-red-400">
        {{ errors.category }}
      </p>
    </div>

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        優先度 <span class="text-red-500">*</span>
      </label>
      <div class="flex items-center space-x-4">
        <input
          v-model.number="formData.priority"
          type="range"
          min="1"
          max="5"
          class="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer dark:bg-gray-700"
        />
        <span class="text-sm font-semibold text-gray-900 dark:text-white min-w-[3rem] text-center">
          {{ formData.priority }}
        </span>
      </div>
      <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
        1（低）〜 5（高）
      </p>
    </div>

    <!-- intent_key（オプション、通常は自動生成） -->
    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        インテントキー
        <span class="text-xs text-gray-500 dark:text-gray-400 ml-2">
          （オプション、自動生成される場合は省略可能）
        </span>
      </label>
      <input
        v-model="formData.intent_key"
        type="text"
        placeholder="例: basic_checkout_time（自動生成される場合は空欄）"
        class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      />
    </div>

    <div class="flex items-center justify-end space-x-3 pt-4">
      <button
        type="button"
        @click="handleCancel"
        class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600 rounded-lg transition-colors"
      >
        キャンセル
      </button>
      <button
        type="submit"
        :disabled="!isValid"
        class="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {{ isEditMode ? '更新' : '作成' }}
      </button>
    </div>
  </form>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import Input from '@/components/common/Input.vue'
import type { FAQ, FAQCreate, FAQCategory, FAQTranslationCreate } from '@/types/faq'
import { SUPPORTED_LANGUAGES } from '@/utils/constants'

const supportedByCode = new Map<string, { name: string; flag: string }>(
  SUPPORTED_LANGUAGES.map(s => [s.code, { name: s.name, flag: s.flag }])
)

interface Props {
  faq?: FAQ | null
  /** C1: 施設設定APIの allowed_faq_languages（空のときは SUPPORTED の全コードにフォールバック） */
  allowedFaqLanguages?: string[]
  /** 施設の言語数上限（null で無制限） */
  languageLimit?: number | null
  /** 他の有効FAQで使用中の言語（編集中FAQは除く） */
  otherFaqLanguages?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  allowedFaqLanguages: () => [],
  languageLimit: null,
  otherFaqLanguages: () => []
})

const emit = defineEmits<{
  submit: [data: FAQCreate]
  cancel: []
}>()

const isEditMode = computed(() => !!props.faq)

/** C1 ∩ SUPPORTED（allowed の順序を維持）。allowed が空なら SUPPORTED 順の全コード */
const baseOrderedCodes = computed(() => {
  const supportedCodes = new Set<string>(SUPPORTED_LANGUAGES.map(s => s.code))
  const alb = props.allowedFaqLanguages
  if (!alb.length) {
    return SUPPORTED_LANGUAGES.map(s => s.code)
  }
  return alb.filter(c => supportedCodes.has(c))
})

/** C3: 新規作成時の既定＝許容リスト先頭（= プラン第一言語）。フォールバックは ja */
const defaultTranslationLanguage = computed(() => baseOrderedCodes.value[0] ?? 'ja')

function labelForCode(code: string): string {
  const s = supportedByCode.get(code)
  if (s) return `${s.flag} ${s.name}`
  return code
}

interface LangRowOption {
  code: string
  label: string
  disabled: boolean
  disabledReason: string
}

function languageRowOptions(rowIndex: number): LangRowOption[] {
  const orderedBase = baseOrderedCodes.value
  const codeSet = new Set<string>(orderedBase)
  formData.value.translations.forEach(t => {
    if (t.language) codeSet.add(t.language)
  })
  const ordered: string[] = []
  for (const c of orderedBase) {
    if (codeSet.has(c)) ordered.push(c)
  }
  for (const c of [...codeSet].sort()) {
    if (!ordered.includes(c)) ordered.push(c)
  }

  const restLangs = new Set<string>()
  formData.value.translations.forEach((t, j) => {
    if (j !== rowIndex && t.language) restLangs.add(t.language)
  })
  const other = new Set(props.otherFaqLanguages || [])
  const lim = props.languageLimit
  const cur = formData.value.translations[rowIndex]?.language
  const allowedStrict = props.allowedFaqLanguages

  return ordered.map(code => {
    let disabled = false
    let disabledReason = ''
    if (allowedStrict.length > 0 && !allowedStrict.includes(code)) {
      disabled = true
      disabledReason = 'プランの対象外です'
    }
    if (lim != null && lim > 0 && code !== cur) {
      const combined = new Set<string>([...other, ...restLangs])
      if (!combined.has(code) && combined.size >= lim) {
        disabled = true
        disabledReason = disabledReason || '言語数の上限に達しています'
      }
    }
    if (code === cur) {
      disabled = false
      disabledReason = ''
    }
    return { code, label: labelForCode(code), disabled, disabledReason }
  })
}

const formData = ref<{
  category: FAQCategory | ''
  intent_key?: string
  translations: FAQTranslationCreate[]
  priority: number
  is_active?: boolean
}>({
  category: '',
  intent_key: undefined,
  translations: [
    {
      language: 'ja',
      question: '',
      answer: ''
    }
  ],
  priority: 3,
  is_active: true
})

const errors = ref<Record<string, string>>({})

// 編集モード時にフォームデータを初期化
watch(() => props.faq, (faq) => {
  const firstLang = defaultTranslationLanguage.value
  if (faq) {
    // 編集モード: FAQのtranslationsからフォームデータを初期化
    formData.value = {
      category: faq.category,
      intent_key: faq.intent_key,
      translations: faq.translations.map(trans => ({
        language: trans.language,
        question: trans.question,
        answer: trans.answer
      })),
      priority: faq.priority,
      is_active: faq.is_active
    }
  } else {
    // 新規作成モード: デフォルト値で初期化
    formData.value = {
      category: '',
      intent_key: undefined,
      translations: [
        {
          language: firstLang,
          question: '',
          answer: ''
        }
      ],
      priority: 3,
      is_active: true
    }
  }
  errors.value = {}
}, { immediate: true })

// 施設設定の取得が遅延した場合、新規下書きの第1言語をプラン先頭に合わせる
watch(
  () => props.allowedFaqLanguages.slice(),
  () => {
    if (props.faq) return
    const t = formData.value.translations[0]
    if (formData.value.translations.length !== 1 || !t) return
    const empty = !t.question.trim() && !t.answer.trim()
    if (!empty) return
    t.language = defaultTranslationLanguage.value
  }
)

const isValid = computed(() => {
  return (
    formData.value.category !== '' &&
    formData.value.translations.length > 0 &&
    formData.value.translations.every(trans => 
      trans.question.trim().length > 0 &&
      trans.answer.trim().length > 0
    ) &&
    formData.value.priority >= 1 &&
    formData.value.priority <= 5 &&
    Object.keys(errors.value).length === 0
  )
})

/** 下書きありか（いずれか入力済み）。外側クリック閉じ防止で参照する */
const isDirty = computed(() => {
  const d = formData.value
  const hasTranslationContent = d.translations.some(
    t => (t.question && t.question.trim() !== '') || (t.answer && t.answer.trim() !== '')
  )
  const hasCategory = d.category !== ''
  const hasIntentKey = typeof d.intent_key === 'string' && d.intent_key.trim() !== ''
  return hasTranslationContent || hasCategory || hasIntentKey
})

defineExpose({ isDirty })

const validateTranslationQuestion = (index: number) => {
  const translation = formData.value.translations[index]
  if (!translation) return
  
  const key = `translation_${index}_question`
  if (translation.question.trim().length === 0) {
    errors.value[key] = '質問文を入力してください'
  } else if (translation.question.length > 500) {
    errors.value[key] = '質問文は500文字以内で入力してください'
  } else {
    delete errors.value[key]
  }
}

const validateTranslationAnswer = (index: number) => {
  const translation = formData.value.translations[index]
  if (!translation) return
  
  const key = `translation_${index}_answer`
  if (translation.answer.trim().length === 0) {
    errors.value[key] = '回答文を入力してください'
  } else if (translation.answer.length > 2000) {
    errors.value[key] = '回答文は2000文字以内で入力してください'
  } else {
    delete errors.value[key]
  }
}

const addTranslation = () => {
  // C3: 同一FAQ内の重複言語を避け、プラン順で最初の未使用コードを選ぶ
  const used = new Set(formData.value.translations.map(t => t.language))
  const pick =
    baseOrderedCodes.value.find(code => !used.has(code)) ??
    defaultTranslationLanguage.value
  formData.value.translations.push({
    language: pick,
    question: '',
    answer: ''
  })
}

const removeTranslation = (index: number) => {
  if (formData.value.translations.length > 1) {
    formData.value.translations.splice(index, 1)
    // エラーも削除
    Object.keys(errors.value).forEach(key => {
      if (key.startsWith(`translation_${index}_`)) {
        delete errors.value[key]
      }
    })
  }
}

const handleSubmit = () => {
  // すべての翻訳をバリデーション
  formData.value.translations.forEach((_, index) => {
    validateTranslationQuestion(index)
    validateTranslationAnswer(index)
  })
  
  if (formData.value.category === '') {
    errors.value.category = 'カテゴリを選択してください'
  } else {
    delete errors.value.category
  }

  if (formData.value.translations.length === 0) {
    errors.value.translations = '最低1つの翻訳が必要です'
  } else {
    delete errors.value.translations
  }

  if (isValid.value && formData.value.category !== '') {
    const submitData: FAQCreate = {
      category: formData.value.category as FAQCategory,
      intent_key: formData.value.intent_key || undefined,
      translations: formData.value.translations.map(trans => ({
        language: trans.language,
        question: trans.question.trim(),
        answer: trans.answer.trim()
      })),
      priority: formData.value.priority,
      is_active: formData.value.is_active
    }
    emit('submit', submitData)
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
/* Component styles */
</style>
