import type { Platform } from '~/types'

export const usePlatforms = () => {
  const platforms = ref<Platform[]>([])
  const loading = ref(false)
  const error = ref<string | null>(null)

  const fetchPlatforms = async () => {
    loading.value = true
    error.value = null
    
    try {
      const { data } = await $fetch<{ data: Platform[] }>('/api/platforms')
      platforms.value = data
    } catch (err) {
      error.value = err instanceof Error ? err.message : '获取平台数据失败'
      console.error('Failed to fetch platforms:', err)
    } finally {
      loading.value = false
    }
  }

  // 自动加载数据
  onMounted(() => {
    fetchPlatforms()
  })

  return {
    platforms: readonly(platforms),
    loading: readonly(loading),
    error: readonly(error),
    fetchPlatforms
  }
}