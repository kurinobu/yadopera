<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4 py-8">
    <div class="w-full max-w-md">
      <!-- ヘッダー -->
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          YadOPERA
        </h1>
        <p class="text-gray-600 dark:text-gray-400">
          言語を選択してください / Please select your language
        </p>
      </div>

      <!-- 言語カードリスト -->
      <div class="space-y-4">
        <LanguageCard
          v-for="language in supportedLanguages"
          :key="language.code"
          :language="language"
          :selected="selectedLanguage?.code === language.code"
          @click="handleLanguageSelect"
        />
      </div>

      <!-- ローディング表示 -->
      <Loading v-if="isLoading" text="読み込み中..." class="mt-8" />

      <!-- エラー表示 -->
      <div
        v-if="error"
        class="mt-4 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
      >
        <p class="text-sm text-red-600 dark:text-red-400">
          {{ error }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { SUPPORTED_LANGUAGES } from '@/utils/constants'
import LanguageCard from '@/components/guest/LanguageCard.vue'
import Loading from '@/components/common/Loading.vue'
import { facilityApi } from '@/api/facility'
import { useFacilityStore } from '@/stores/facility'

const route = useRoute()
const router = useRouter()
const facilityStore = useFacilityStore()

const facilityId = computed(() => route.params.facilityId as string)
const supportedLanguages = ref<typeof SUPPORTED_LANGUAGES[number][]>([...SUPPORTED_LANGUAGES])
const selectedLanguage = ref<typeof SUPPORTED_LANGUAGES[number] | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)

// 施設情報を取得（slugまたはIDから）
onMounted(async () => {
  try {
    isLoading.value = true
    error.value = null
    
    // 施設情報を取得
    const slug = facilityId.value
    const response = await facilityApi.getFacility(slug)
    
    // 施設情報をstoreに保存
    facilityStore.setFacility(response.facility)
    facilityStore.setTopQuestions(response.top_questions)
    
    // プランに応じた利用可能言語を取得
    const availableLanguages = response.facility.available_languages || ['en']
    
    // SUPPORTED_LANGUAGESから、利用可能な言語のみをフィルタリング
    const filteredLanguages = SUPPORTED_LANGUAGES.filter(lang => 
      availableLanguages.includes(lang.code)
    )
    
    // 利用可能な言語がない場合、デフォルトで英語を表示
    if (filteredLanguages.length === 0) {
      supportedLanguages.value = [...SUPPORTED_LANGUAGES]
    } else {
      supportedLanguages.value = filteredLanguages
    }
  } catch (err) {
    error.value = '施設情報の取得に失敗しました'
    console.error('Facility fetch error:', err)
    // エラー時はデフォルトで英語を表示（既存の動作を維持）
    supportedLanguages.value = [...SUPPORTED_LANGUAGES]
  } finally {
    isLoading.value = false
  }
})

const handleLanguageSelect = (language: typeof SUPPORTED_LANGUAGES[number]) => {
  selectedLanguage.value = language
  
  // ウェルカム画面に遷移
  router.push({
    name: 'Welcome',
    params: { facilityId: facilityId.value },
    query: { lang: language.code }
  })
}
</script>

<style scoped>
/* Component styles */
</style>


