/**
 * ヘルプシステム状態管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { helpApi } from '@/api/help'
import type {
  Faq,
  FaqListResponse,
  FaqSearchResponse,
  ChatMessage,
  ChatRequest,
  ChatResponse,
  HelpTab,
  FaqCategory,
} from '@/types/help'

export const useHelpStore = defineStore('help', () => {
  // State
  const faqs = ref<Faq[]>([])
  const categories = ref<string[]>([])
  const searchResults = ref<Faq[]>([])
  const searchQuery = ref('')
  const selectedCategory = ref<FaqCategory | null>(null)
  const currentTab = ref<HelpTab>('faq')
  const chatMessages = ref<ChatMessage[]>([])
  const isLoading = ref(false)
  const isSearching = ref(false)
  const isChatting = ref(false)
  const language = ref<'ja' | 'en'>('ja')
  const isModalOpen = ref(false)

  // Getters
  const filteredFaqs = computed(() => {
    if (selectedCategory.value) {
      return faqs.value.filter(faq => faq.category === selectedCategory.value)
    }
    return faqs.value
  })

  const hasSearchResults = computed(() => searchResults.value.length > 0)
  const hasChatMessages = computed(() => chatMessages.value.length > 0)

  // Actions
  /**
   * FAQ一覧取得
   */
  async function fetchFaqs(category?: string) {
    try {
      isLoading.value = true
      const response: FaqListResponse = await helpApi.getFaqs({
        category: category || undefined,
        language: language.value,
      })
      faqs.value = response.faqs
      categories.value = response.categories
    } catch (error) {
      console.error('Failed to fetch FAQs:', error)
      throw error
    } finally {
      isLoading.value = false
    }
  }

  /**
   * FAQ検索
   */
  async function searchFaqs(query: string) {
    if (!query || query.length < 2) {
      searchResults.value = []
      searchQuery.value = ''
      return
    }

    try {
      isSearching.value = true
      searchQuery.value = query
      const response: FaqSearchResponse = await helpApi.searchFaqs({
        query,
        language: language.value,
        limit: 10,
      })
      searchResults.value = response.results
    } catch (error) {
      console.error('Failed to search FAQs:', error)
      throw error
    } finally {
      isSearching.value = false
    }
  }

  /**
   * カテゴリフィルタ設定
   */
  function setCategory(category: FaqCategory | null) {
    selectedCategory.value = category
  }

  /**
   * タブ切り替え
   */
  function setTab(tab: HelpTab) {
    currentTab.value = tab
  }

  /**
   * チャットメッセージ送信
   */
  async function sendChatMessage(message: string) {
    // ユーザーメッセージを追加
    const userMessage: ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: message,
      timestamp: new Date().toISOString(),
    }
    chatMessages.value.push(userMessage)

    try {
      isChatting.value = true
      const request: ChatRequest = {
        message,
        language: language.value,
      }
      const response: ChatResponse = await helpApi.sendChat(request)

      // AI応答を追加
      const aiMessage: ChatMessage = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: response.timestamp,
        related_faqs: response.related_faqs,
        related_url: response.related_url,
      }
      chatMessages.value.push(aiMessage)
    } catch (error) {
      console.error('Failed to send chat message:', error)
      // エラーメッセージを追加
      const errorMessage: ChatMessage = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: language.value === 'ja'
          ? '申し訳ございません。エラーが発生しました。しばらく待ってから再度お試しください。'
          : 'Sorry, an error occurred. Please try again later.',
        timestamp: new Date().toISOString(),
      }
      chatMessages.value.push(errorMessage)
      throw error
    } finally {
      isChatting.value = false
    }
  }

  /**
   * チャット履歴クリア
   */
  function clearChat() {
    chatMessages.value = []
  }

  /**
   * 言語切り替え
   */
  function setLanguage(lang: 'ja' | 'en') {
    language.value = lang
    // 言語変更時はFAQを再取得
    fetchFaqs(selectedCategory.value || undefined)
  }

  /**
   * モーダル開閉
   */
  function openModal() {
    isModalOpen.value = true
    // モーダルを開いた時にFAQを取得
    if (faqs.value.length === 0) {
      fetchFaqs()
    }
  }

  function closeModal() {
    isModalOpen.value = false
  }

  /**
   * 初期化
   */
  function reset() {
    faqs.value = []
    categories.value = []
    searchResults.value = []
    searchQuery.value = ''
    selectedCategory.value = null
    currentTab.value = 'faq'
    chatMessages.value = []
    isLoading.value = false
    isSearching.value = false
    isChatting.value = false
  }

  return {
    // State
    faqs,
    categories,
    searchResults,
    searchQuery,
    selectedCategory,
    currentTab,
    chatMessages,
    isLoading,
    isSearching,
    isChatting,
    language,
    isModalOpen,
    // Getters
    filteredFaqs,
    hasSearchResults,
    hasChatMessages,
    // Actions
    fetchFaqs,
    searchFaqs,
    setCategory,
    setTab,
    sendChatMessage,
    clearChat,
    setLanguage,
    openModal,
    closeModal,
    reset,
  }
})

