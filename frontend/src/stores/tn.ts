import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TnEntry, TnFilter } from '@/types/tn'

export const useTnStore = defineStore('tn', () => {
  const tnList = ref<TnEntry[]>([])
  const currentTn = ref<TnEntry | null>(null)
  const filter = ref<TnFilter>({
    keyword: '',
    family: '',
    origin: '',
    mge_type: undefined,
    page: 1,
    page_size: 20
  })
  const total = ref(0)
  const loading = ref(false)

  function setTnList(list: TnEntry[], count: number) {
    tnList.value = list
    total.value = count
  }

  function setCurrentTn(tn: TnEntry | null) {
    currentTn.value = tn
  }

  function setFilter(newFilter: Partial<TnFilter>) {
    filter.value = { ...filter.value, ...newFilter }
  }

  function resetFilter() {
    filter.value = {
      keyword: '',
      family: '',
      origin: '',
      mge_type: undefined,
      page: 1,
      page_size: 20
    }
  }

  function setLoading(value: boolean) {
    loading.value = value
  }

  return {
    tnList,
    currentTn,
    filter,
    total,
    loading,
    setTnList,
    setCurrentTn,
    setFilter,
    resetFilter,
    setLoading
  }
})
