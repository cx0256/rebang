import type { HotItem, Platform, Category, HotItemsQuery, PaginatedResponse, TrendingItem, SearchResult, Statistics, PlatformStats } from '~/types'

export const useHotList = () => {
  const { $api } = useNuxtApp()
  
  // 状态管理
  const platforms = useState<Platform[]>('hotlist.platforms', () => [])
  const categories = useState<Category[]>('hotlist.categories', () => [])
  const hotItems = useState<HotItem[]>('hotlist.hotItems', () => [])
  const currentPlatform = useState<Platform | null>('hotlist.currentPlatform', () => null)
  const currentCategory = useState<Category | null>('hotlist.currentCategory', () => null)
  const loading = useState<boolean>('hotlist.loading', () => false)
  const error = useState<string | null>('hotlist.error', () => null)
  
  // 获取所有平台
  const fetchPlatforms = async (refresh = false) => {
    if (platforms.value.length > 0 && !refresh) {
      return platforms.value
    }
    
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get('/api/v1/platforms')
      
      if (response.success && response.data) {
        platforms.value = response.data
        return response.data
      } else {
        throw new Error(response.message || '获取平台列表失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch platforms error:', err)
      return []
    } finally {
      loading.value = false
    }
  }
  
  // 获取分类列表
  const fetchCategories = async (platformId?: number, refresh = false) => {
    const cacheKey = platformId ? `platform-${platformId}` : 'all'
    
    if (categories.value.length > 0 && !refresh && !platformId) {
      return categories.value
    }
    
    try {
      loading.value = true
      error.value = null
      
      const url = platformId ? `/api/v1/platforms/${platformId}/categories` : '/api/v1/categories'
      const response = await $api.get(url)
      
      if (response.success && response.data) {
        if (!platformId) {
          categories.value = response.data
        }
        return response.data
      } else {
        throw new Error(response.message || '获取分类列表失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch categories error:', err)
      return []
    } finally {
      loading.value = false
    }
  }
  
  // 获取热门条目
  const fetchHotItems = async (query: HotItemsQuery = {}, refresh = false) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get('/api/v1/hot-items', { params: query })
      
      if (response.success && response.data) {
        if (!query.page || query.page === 1) {
          hotItems.value = response.data.items
        } else {
          // 分页加载，追加数据
          hotItems.value.push(...response.data.items)
        }
        return response.data as PaginatedResponse<HotItem>
      } else {
        throw new Error(response.message || '获取热门条目失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch hot items error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 获取所有热榜
  const fetchAllHotLists = async (refresh = false) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get('/api/v1/hot')
      
      if (response.success && response.data) {
        return response.data
      } else {
        throw new Error(response.message || '获取热榜失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch all hot lists error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 获取平台热榜
  const fetchPlatformHotList = async (platformName: string, refresh = false) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get(`/api/v1/hot/${platformName}`)
      
      if (response.success && response.data) {
        return response.data
      } else {
        throw new Error(response.message || '获取平台热榜失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch platform hot list error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 获取分类热榜
  const fetchCategoryHotList = async (platformName: string, categoryName: string, refresh = false) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get(`/api/v1/hot/${platformName}/${categoryName}`)
      
      if (response.success && response.data) {
        return response.data
      } else {
        throw new Error(response.message || '获取分类热榜失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch category hot list error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 获取单个热门条目
  const fetchHotItem = async (id: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get(`/api/v1/hot-items/${id}`)
      
      if (response.success && response.data) {
        return response.data as HotItem
      } else {
        throw new Error(response.message || '获取热门条目失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch hot item error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 获取今日趋势
  const fetchTodayTrending = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get('/api/v1/hot-items/trending/today')
      
      if (response.success && response.data) {
        return response.data as TrendingItem[]
      } else {
        throw new Error(response.message || '获取今日趋势失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch today trending error:', err)
      return []
    } finally {
      loading.value = false
    }
  }
  
  // 获取本周趋势
  const fetchWeekTrending = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get('/api/v1/hot-items/trending/week')
      
      if (response.success && response.data) {
        return response.data as TrendingItem[]
      } else {
        throw new Error(response.message || '获取本周趋势失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch week trending error:', err)
      return []
    } finally {
      loading.value = false
    }
  }
  
  // 搜索热门条目
  const searchHotItems = async (query: string, filters: Partial<HotItemsQuery> = {}) => {
    try {
      loading.value = true
      error.value = null
      
      const params = {
        search: query,
        ...filters
      }
      
      const response = await $api.get('/api/v1/hot-items/search', { params })
      
      if (response.success && response.data) {
        return response.data as SearchResult
      } else {
        throw new Error(response.message || '搜索失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Search hot items error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 获取统计数据
  const fetchStatistics = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get('/api/v1/hot-items/stats')
      
      if (response.success && response.data) {
        return response.data as Statistics
      } else {
        throw new Error(response.message || '获取统计数据失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch statistics error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 获取平台统计
  const fetchPlatformStats = async (platformId: number) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await $api.get(`/api/v1/hot-items/stats/platform/${platformId}`)
      
      if (response.success && response.data) {
        return response.data as PlatformStats
      } else {
        throw new Error(response.message || '获取平台统计失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Fetch platform stats error:', err)
      return null
    } finally {
      loading.value = false
    }
  }
  
  // 刷新缓存
  const refreshCache = async (key?: string) => {
    try {
      loading.value = true
      error.value = null
      
      const url = key ? `/api/v1/cache/refresh/${key}` : '/api/v1/cache/refresh'
      const response = await $api.post(url)
      
      if (response.success) {
        return { success: true, message: '缓存刷新成功' }
      } else {
        throw new Error(response.message || '缓存刷新失败')
      }
    } catch (err: any) {
      error.value = err.message
      console.error('Refresh cache error:', err)
      return { success: false, error: err.message }
    } finally {
      loading.value = false
    }
  }
  
  // 设置当前平台
  const setCurrentPlatform = (platform: Platform | null) => {
    currentPlatform.value = platform
    currentCategory.value = null // 重置分类
  }
  
  // 设置当前分类
  const setCurrentCategory = (category: Category | null) => {
    currentCategory.value = category
  }
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  // 重置状态
  const reset = () => {
    hotItems.value = []
    currentPlatform.value = null
    currentCategory.value = null
    error.value = null
    loading.value = false
  }
  
  return {
    // 状态
    platforms: readonly(platforms),
    categories: readonly(categories),
    hotItems: readonly(hotItems),
    currentPlatform: readonly(currentPlatform),
    currentCategory: readonly(currentCategory),
    loading: readonly(loading),
    error: readonly(error),
    
    // 方法
    fetchPlatforms,
    fetchCategories,
    fetchHotItems,
    fetchAllHotLists,
    fetchPlatformHotList,
    fetchCategoryHotList,
    fetchHotItem,
    fetchTodayTrending,
    fetchWeekTrending,
    searchHotItems,
    fetchStatistics,
    fetchPlatformStats,
    refreshCache,
    setCurrentPlatform,
    setCurrentCategory,
    clearError,
    reset
  }
}