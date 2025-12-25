/**
 * 施設情報状態管理
 */

import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Facility, TopQuestion } from '@/types/facility'

export const useFacilityStore = defineStore('facility', () => {
  // State
  const currentFacility = ref<Facility | null>(null)
  const topQuestions = ref<TopQuestion[]>([])

  // Actions
  function setFacility(facility: Facility | null) {
    currentFacility.value = facility
  }

  function setTopQuestions(questions: any[]) {
    topQuestions.value = questions
  }

  function clearFacility() {
    currentFacility.value = null
    topQuestions.value = []
  }

  return {
    currentFacility,
    topQuestions,
    setFacility,
    setTopQuestions,
    clearFacility
  }
})

