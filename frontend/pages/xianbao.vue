<template>
  <div class="min-h-screen bg-white dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-6xl mx-auto px-4">
        <div class="flex justify-between items-center h-14">
          <div class="flex items-center space-x-3">
            <button 
              @click="goBack"
              class="flex items-center space-x-1 text-gray-500 dark:text-gray-400 hover:text-blue-600 dark:hover:text-blue-400 text-sm"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              <span>返回热榜</span>
            </button>
            <div class="h-4 w-px bg-gray-300 dark:bg-gray-600"></div>
            <h1 class="text-lg font-bold text-blue-600 dark:text-blue-400">线报酷</h1>
          </div>
          <div class="flex items-center space-x-4">
            <span class="text-xs text-gray-500 dark:text-gray-400">实时更新优惠信息</span>
            <ThemeToggle />
          </div>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-6xl mx-auto">
      <!-- Stats Bar -->
      <div class="bg-gray-50 dark:bg-gray-800 px-4 py-3 border-b border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center text-sm">
          <div class="flex items-center space-x-6">
            <span class="text-gray-600 dark:text-gray-400">今日更新: <span class="font-semibold text-blue-600 dark:text-blue-400">{{ todayCount }}</span> 条</span>
            <span class="text-gray-600 dark:text-gray-400">总计: <span class="font-semibold">{{ totalCount }}</span> 条线报</span>
          </div>
          <div class="flex items-center space-x-4">
            <button 
              @click="refreshItems"
              class="flex items-center space-x-1 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
              </svg>
              <span>刷新</span>
            </button>
            <span class="text-xs text-gray-500 dark:text-gray-400">最后更新: {{ lastUpdateTime }}</span>
          </div>
        </div>
      </div>

      <!-- Loading Skeleton -->
      <div v-if="loading" class="px-4">
        <div v-for="i in 8" :key="i" class="border-b border-gray-200 dark:border-gray-700 py-4 animate-pulse">
          <div class="flex justify-between items-start mb-2">
            <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded w-3/4"></div>
            <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-16"></div>
          </div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/2 mb-2"></div>
          <div class="flex justify-between items-center">
            <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-20"></div>
            <div class="h-6 bg-gray-300 dark:bg-gray-600 rounded w-16"></div>
          </div>
        </div>
      </div>

      <!-- Deal List -->
      <div v-else-if="items.length > 0" class="divide-y divide-gray-200 dark:divide-gray-700">
        <div 
          v-for="item in items" 
          :key="item.id"
          class="px-4 py-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors cursor-pointer"
          @click="openDeal(item)"
        >
          <div class="flex justify-between items-start mb-2">
            <h3 class="text-base font-medium text-gray-900 dark:text-gray-100 hover:text-blue-600 dark:hover:text-blue-400 line-clamp-2 flex-1 mr-4">
              {{ item.title }}
            </h3>
            <div class="flex items-center space-x-2 text-xs text-gray-500 dark:text-gray-400 flex-shrink-0">
              <span>{{ formatTime(item.publishTime) }}</span>
              <span v-if="item.isHot" class="bg-red-100 text-red-600 dark:bg-red-900 dark:text-red-400 px-1.5 py-0.5 rounded">热门</span>
              <span v-if="item.isNew" class="bg-green-100 text-green-600 dark:bg-green-900 dark:text-green-400 px-1.5 py-0.5 rounded">新</span>
            </div>
          </div>
          
          <p v-if="item.description" class="text-sm text-gray-600 dark:text-gray-400 mb-2 line-clamp-1">
            {{ item.description }}
          </p>
          
          <div class="flex justify-between items-center text-xs">
            <div class="flex items-center space-x-4 text-gray-500 dark:text-gray-400">
              <span class="flex items-center space-x-1">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M10 12a2 2 0 100-4 2 2 0 000 4z"></path>
                  <path fill-rule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clip-rule="evenodd"></path>
                </svg>
                <span>{{ item.views || 0 }}</span>
              </span>
              <span class="flex items-center space-x-1">
                <svg class="w-3 h-3" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M3.172 5.172a4 4 0 015.656 0L10 6.343l1.172-1.171a4 4 0 115.656 5.656L10 17.657l-6.828-6.829a4 4 0 010-5.656z" clip-rule="evenodd"></path>
                </svg>
                <span>{{ item.likes || 0 }}</span>
              </span>
              <span>来源: {{ item.source }}</span>
              <span v-if="item.expiryDate" class="text-red-500 dark:text-red-400">
                {{ formatExpiryDate(item.expiryDate) }}
              </span>
            </div>
            <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium" :class="getCategoryClass(item.category)">
              {{ getCategoryName(item.category) }}
            </span>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-16 px-4">
        <svg class="mx-auto h-16 w-16 text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">暂无线报信息</h3>
        <p class="text-gray-500 dark:text-gray-400">请稍后再试或刷新页面</p>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !loading" class="text-center py-6 border-t border-gray-200 dark:border-gray-700">
        <button 
          @click="loadMore"
          class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded transition-colors"
        >
          加载更多
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// SEO
useHead({
  title: '线报酷 - 优惠促销信息分享',
  meta: [
    { name: 'description', content: '专注线报活动与优惠促销分享的线报网站，实时更新各类优惠信息' }
  ]
})

const router = useRouter()

// State
const items = ref([])
const loading = ref(false)
const error = ref(null)
const currentPage = ref(1)
const hasMore = ref(true)

// Stats
const todayCount = ref(0)
const totalCount = ref(0)
const lastUpdateTime = ref('')

// Computed
const currentTime = computed(() => {
  const now = new Date()
  return now.toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
})

// Methods
const goBack = () => {
  router.push('/')
}

const refreshItems = () => {
  fetchItems(1)
}

const getCategoryName = (category) => {
  const categoryMap = {
    shopping: '购物',
    food: '美食',
    digital: '数码',
    travel: '旅游',
    entertainment: '娱乐',
    finance: '金融',
    game: '游戏',
    other: '其他'
  }
  return categoryMap[category] || '其他'
}

const getCategoryClass = (category) => {
  const classMap = {
    shopping: 'bg-blue-50 text-blue-600 dark:bg-blue-900 dark:text-blue-300',
    food: 'bg-green-50 text-green-600 dark:bg-green-900 dark:text-green-300',
    digital: 'bg-purple-50 text-purple-600 dark:bg-purple-900 dark:text-purple-300',
    travel: 'bg-yellow-50 text-yellow-600 dark:bg-yellow-900 dark:text-yellow-300',
    entertainment: 'bg-pink-50 text-pink-600 dark:bg-pink-900 dark:text-pink-300',
    finance: 'bg-indigo-50 text-indigo-600 dark:bg-indigo-900 dark:text-indigo-300',
    game: 'bg-red-50 text-red-600 dark:bg-red-900 dark:text-red-300',
    other: 'bg-gray-50 text-gray-600 dark:bg-gray-900 dark:text-gray-300'
  }
  return classMap[category] || classMap.other
}

const formatTime = (time) => {
  const now = new Date()
  const publishTime = new Date(time)
  const diff = now - publishTime
  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (minutes < 60) {
    return `${minutes}分钟前`
  } else if (hours < 24) {
    return `${hours}小时前`
  } else {
    return `${days}天前`
  }
}

const formatExpiryDate = (date) => {
  const now = new Date()
  const expiry = new Date(date)
  const diff = expiry - now
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)
  
  if (diff < 0) {
    return '已过期'
  } else if (hours < 24) {
    return `${hours}小时后过期`
  } else {
    return `${days}天后过期`
  }
}

const openDeal = (item) => {
  // Simulate opening deal link
  window.open(item.link || '#', '_blank')
}

const fetchItems = async (page = 1) => {
  loading.value = true
  error.value = null
  
  try {
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 800))
    
    // Mock data - more realistic deal titles
    const mockItems = [
      {
        id: 1,
        title: '【免费领取】支付宝扫码领红包 每天可领1-99元',
        description: '支付宝官方活动，每天扫码可领随机红包，线下支付自动抵扣',
        category: 'finance',
        publishTime: new Date(Date.now() - 15 * 60000),
        expiryDate: null,
        source: '支付宝官方',
        views: 2341,
        likes: 156,
        isHot: true,
        isNew: false,
        link: 'https://example.com'
      },
      {
        id: 2,
        title: '京东PLUS会员年卡5折 原价198现价99元',
        description: '京东PLUS会员年卡限时5折，享全年免邮、专属优惠等特权',
        category: 'shopping',
        publishTime: new Date(Date.now() - 45 * 60000),
        expiryDate: new Date(Date.now() + 2 * 24 * 60 * 60000),
        source: '京东',
        views: 1876,
        likes: 89,
        isHot: false,
        isNew: true,
        link: 'https://example.com'
      },
      {
        id: 3,
        title: '美团外卖新用户20元无门槛券 限时领取',
        description: '美团外卖新用户专享，注册即送20元无门槛优惠券',
        category: 'food',
        publishTime: new Date(Date.now() - 1.5 * 60 * 60000),
        expiryDate: new Date(Date.now() + 5 * 24 * 60 * 60000),
        source: '美团',
        views: 1234,
        likes: 67,
        isHot: false,
        isNew: false,
        link: 'https://example.com'
      },
      {
        id: 4,
        title: '腾讯视频VIP 3个月19.9元 限时特惠',
        description: '腾讯视频VIP会员3个月套餐特价，海量高清影视随意看',
        category: 'entertainment',
        publishTime: new Date(Date.now() - 3 * 60 * 60000),
        expiryDate: new Date(Date.now() + 3 * 24 * 60 * 60000),
        source: '腾讯视频',
        views: 987,
        likes: 45,
        isHot: false,
        isNew: false,
        link: 'https://example.com'
      },
      {
        id: 5,
        title: '王者荣耀皮肤免费领 限时活动进行中',
        description: '王者荣耀官方活动，完成任务即可免费获得限定皮肤',
        category: 'game',
        publishTime: new Date(Date.now() - 4 * 60 * 60000),
        expiryDate: new Date(Date.now() + 7 * 24 * 60 * 60000),
        source: '王者荣耀',
        views: 3456,
        likes: 234,
        isHot: true,
        isNew: false,
        link: 'https://example.com'
      },
      {
        id: 6,
        title: '携程酒店满300减100 全国通用不限时间',
        description: '携程APP预订酒店满300立减100，全国酒店通用',
        category: 'travel',
        publishTime: new Date(Date.now() - 6 * 60 * 60000),
        expiryDate: new Date(Date.now() + 10 * 24 * 60 * 60000),
        source: '携程',
        views: 654,
        likes: 32,
        isHot: false,
        isNew: false,
        link: 'https://example.com'
      },
      {
        id: 7,
        title: '拼多多现金大转盘 每天3次机会最高888元',
        description: '拼多多现金大转盘活动，每天3次抽奖机会，最高可得888元现金',
        category: 'shopping',
        publishTime: new Date(Date.now() - 8 * 60 * 60000),
        expiryDate: new Date(Date.now() + 1 * 24 * 60 * 60000),
        source: '拼多多',
        views: 2109,
        likes: 123,
        isHot: false,
        isNew: true,
        link: 'https://example.com'
      },
      {
        id: 8,
        title: '招商银行信用卡新户礼 最高500元京东卡',
        description: '招商银行信用卡新用户专享，成功申请可获得最高500元京东购物卡',
        category: 'finance',
        publishTime: new Date(Date.now() - 10 * 60 * 60000),
        expiryDate: new Date(Date.now() + 15 * 24 * 60 * 60000),
        source: '招商银行',
        views: 876,
        likes: 54,
        isHot: false,
        isNew: false,
        link: 'https://example.com'
      }
    ]
    
    if (page === 1) {
      items.value = mockItems
      // Update stats
      todayCount.value = mockItems.filter(item => {
        const today = new Date()
        const itemDate = new Date(item.publishTime)
        return itemDate.toDateString() === today.toDateString()
      }).length
      totalCount.value = 1247 // Mock total count
      lastUpdateTime.value = currentTime.value
    } else {
      const newItems = mockItems.map(item => ({ ...item, id: item.id + (page - 1) * 8 }))
      items.value.push(...newItems)
    }
    
    hasMore.value = page < 3 // Simulate 3 pages of data
    currentPage.value = page
  } catch (err) {
    error.value = 'Failed to load deals'
    console.error('Error fetching items:', err)
  } finally {
    loading.value = false
  }
}

const loadMore = () => {
  fetchItems(currentPage.value + 1)
}

// Initialize
onMounted(() => {
  fetchItems(1)
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>