<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <Input
      v-model="formData.question"
      type="textarea"
      label="質問文"
      placeholder="例: What is the WiFi password?"
      :required="true"
      :maxlength="200"
      :rows="3"
      hint="200文字以内推奨"
      :error="errors.question"
      @blur="validateQuestion"
    />

    <Input
      v-model="formData.answer"
      type="textarea"
      label="回答文"
      placeholder="例: The WiFi password is guest2024. The SSID is TokyoGuesthouse_WiFi."
      :required="true"
      :maxlength="200"
      :rows="4"
      hint="200文字以内推奨"
      :error="errors.answer"
      @blur="validateAnswer"
    />

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

    <div>
      <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
        言語
      </label>
      <select
        v-model="formData.language"
        class="block w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
      >
        <option value="en">英語</option>
        <option value="ja">日本語</option>
      </select>
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
import type { FAQ, FAQCreate, FAQCategory } from '@/types/faq'

interface Props {
  faq?: FAQ | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  submit: [data: FAQCreate]
  cancel: []
}>()

const isEditMode = computed(() => !!props.faq)

const formData = ref<Omit<FAQCreate, 'category'> & { category: FAQCategory | ''; language: string }>({
  category: '',
  language: 'en',
  question: '',
  answer: '',
  priority: 3
})

const errors = ref<Partial<Record<keyof FAQCreate, string>>>({})

// 編集モード時にフォームデータを初期化
watch(() => props.faq, (faq) => {
  if (faq) {
    formData.value = {
      category: faq.category,
      language: faq.language,
      question: faq.question,
      answer: faq.answer,
      priority: faq.priority
    }
  } else {
    formData.value = {
      category: '',
      language: 'en',
      question: '',
      answer: '',
      priority: 3
    }
  }
  errors.value = {}
}, { immediate: true })

const isValid = computed(() => {
  return (
    formData.value.question.trim().length > 0 &&
    formData.value.answer.trim().length > 0 &&
    formData.value.category !== '' &&
    formData.value.priority >= 1 &&
    formData.value.priority <= 5 &&
    Object.keys(errors.value).length === 0
  )
})

const validateQuestion = () => {
  if (formData.value.question.trim().length === 0) {
    errors.value.question = '質問文を入力してください'
  } else if (formData.value.question.length > 200) {
    errors.value.question = '質問文は200文字以内で入力してください'
  } else {
    delete errors.value.question
  }
}

const validateAnswer = () => {
  if (formData.value.answer.trim().length === 0) {
    errors.value.answer = '回答文を入力してください'
  } else if (formData.value.answer.length > 200) {
    errors.value.answer = '回答文は200文字以内で入力してください'
  } else {
    delete errors.value.answer
  }
}

const handleSubmit = () => {
  validateQuestion()
  validateAnswer()
  
  if (formData.value.category === '') {
    errors.value.category = 'カテゴリを選択してください'
  } else {
    delete errors.value.category
  }

  if (isValid.value && formData.value.category !== '') {
    emit('submit', {
      category: formData.value.category as FAQCategory,
      language: formData.value.language,
      question: formData.value.question.trim(),
      answer: formData.value.answer.trim(),
      priority: formData.value.priority
    })
  }
}

const handleCancel = () => {
  emit('cancel')
}
</script>

<style scoped>
/* Component styles */
</style>


