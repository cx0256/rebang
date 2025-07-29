<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <div class="flex items-center space-x-4">
            <button 
              @click="goBack"
              class="flex items-center space-x-2 text-gray-600 dark:text-gray-300 hover:text-purple-600 dark:hover:text-purple-400 transition-colors"
            >
              <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18"></path>
              </svg>
              <span>Back to Hot List</span>
            </button>
            <div class="h-6 w-px bg-gray-300 dark:bg-gray-600"></div>
            <h1 class="text-xl font-bold text-purple-600 dark:text-purple-400">线报酷</h1>
          </div>
          <ThemeToggle />
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <!-- Search and Filters -->
      <div class="mb-8">
        <div class="flex flex-col lg:flex-row gap-4 mb-6">
          <!-- Search -->
          <div class="flex-1">
            <div class="relative">
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Search deals and promotions..."
                class="w-full pl-10 pr-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
              <svg class="absolute left-3 top-3.5 h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
          </div>
          
          <!-- Category Filter -->
          <div class="lg:w-48">
            <select 
              v-model="selectedCategory"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              <option value="shopping">Shopping</option>
              <option value="food">Food & Dining</option>
              <option value="digital">Digital Products</option>
              <option value="travel">Travel</option>
              <option value="entertainment">Entertainment</option>
              <option value="finance">Finance</option>
              <option value="other">Other</option>
            </select>
          </div>
          
          <!-- Sort -->
          <div class="lg:w-48">
            <select 
              v-model="sortBy"
              class="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="latest">Latest</option>
              <option value="popular">Most Popular</option>
              <option value="expiring">Expiring Soon</option>
            </select>
          </div>
        </div>
        
        <!-- Hot Tags -->
        <div class="flex flex-wrap gap-2">
          <span class="text-sm text-gray-600 dark:text-gray-400 mr-2">Hot Tags:</span>
          <button 
            v-for="tag in hotTags" 
            :key="tag"
            @click="searchQuery = tag"
            class="px-3 py-1 text-xs bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 rounded-full hover:bg-purple-200 dark:hover:bg-purple-800 transition-colors"
          >
            {{ tag }}
          </button>
        </div>
      </div>

      <!-- Loading Skeleton -->
      <div v-if="loading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div v-for="i in 6" :key="i" class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-pulse">
          <div class="h-4 bg-gray-300 dark:bg-gray-600 rounded mb-4"></div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded mb-2"></div>
          <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded mb-4 w-3/4"></div>
          <div class="flex justify-between items-center">
            <div class="h-3 bg-gray-300 dark:bg-gray-600 rounded w-1/4"></div>
            <div class="h-8 bg-gray-300 dark:bg-gray-600 rounded w-20"></div>
          </div>
        </div>
      </div>

      <!-- Deal Cards -->
      <div v-else-if="filteredItems.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        <div 
          v-for="item in filteredItems" 
          :key="item.id"
          class="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow duration-200"
        >
          <div class="p-6">
            <!-- Header -->
            <div class="flex justify-between items-start mb-3">
              <span class="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium" :class="getCategoryClass(item.category)">
                {{ getCategoryName(item.category) }}
              </span>
              <span class="text-xs text-gray-500 dark:text-gray-400">{{ formatTime(item.publishTime) }}</span>
            </div>
            
            <!-- Title -->
            <h3 class="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2 line-clamp-2">
              {{ item.title }}
            </h3>
            
            <!-- Description -->
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-3">
              {{ item.description }}
            </p>
            
            <!-- Meta Info -->
            <div class="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400 mb-4">
              <div class="flex items-center space-x-4">
                <span>👀 {{ item.views }}</span>
                <span>👍 {{ item.likes }}</span>
                <span>💬 {{ item.comments }}</span>
              </div>
              <span v-if="item.expiryDate" class="text-red-500 dark:text-red-400">
                {{ formatExpiryDate(item.expiryDate) }}
              </span>
            </div>
            
            <!-- Footer -->
            <div class="flex justify-between items-center">
              <span class="text-xs text-gray-500 dark:text-gray-400">
                来源: {{ item.source }}
              </span>
              <button 
                @click="openDeal(item)"
                class="px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white text-sm font-medium rounded-lg transition-colors"
              >
                立即查看
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div v-else class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
        </svg>
        <h3 class="text-lg font-medium text-gray-900 dark:text-gray-100 mb-2">No deals found</h3>
        <p class="text-gray-500 dark:text-gray-400">Try adjusting your search or filter criteria</p>
      </div>

      <!-- Load More -->
      <div v-if="hasMore && !loading" class="text-center mt-8">
        <button 
          @click="loadMore"
          class="px-6 py-3 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          Load More
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
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
const searchQuery = ref('')
const selectedCategory = ref('')
const sortBy = ref('latest')

// Hot tags
const hotTags = ref(['免费领取', '限时优惠', '满减活动', '新用户福利', '积分兑换'])

// Computed
const filteredItems = computed(() => {
  let filtered = [...items.value]
  
  // Filter by search query
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(item => 
      item.title.toLowerCase().includes(query) ||
      item.description.toLowerCase().includes(query)
    )
  }
  
  // Filter by category
  if (selectedCategory.value) {
    filtered = filtered.filter(item => item.category === selectedCategory.value)
  }
  
  // Sort
  if (sortBy.value === 'popular') {
    filtered.sort((a, b) => b.views - a.views)
  } else if (sortBy.value === 'expiring') {
    filtered.sort((a, b) => {
      if (!a.expiryDate) return 1
      if (!b.expiryDate) return -1
      return new Date(a.expiryDate) - new Date(b.expiryDate)
    })
  } else {
    filtered.sort((a, b) => new Date(b.publishTime) - new Date(a.publishTime))
  }
  
  return filtered
})

// Methods
const goBack = () => {
  router.push('/')
}

const getCategoryName = (category) => {
  const categoryMap = {
    shopping: '购物优惠',
    food: '美食餐饮',
    digital: '数码产品',
    travel: '旅游出行',
    entertainment: '娱乐休闲',
    finance: '金融理财',
    other: '其他'
  }
  return categoryMap[category] || '其他'
}

const getCategoryClass = (category) => {
  const classMap = {
    shopping: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300',
    food: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300',
    digital: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300',
    travel: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300',
    entertainment: 'bg-pink-100 text-pink-800 dark:bg-pink-900 dark:text-pink-300',
    finance: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300',
    other: 'bg-gray-100 text-gray-800 dark:bg-gray-900 dark:text-gray-300'
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
    await new Promise(resolve => setTimeout(resolve, 1000))
    
    // Mock data
    const mockItems = [
      {
        id: 1,
        title: '京东PLUS会员年卡限时5折优惠',
        description: '原价198元的京东PLUS会员年卡现在只需99元，享受全年免费配送、专属优惠券等特权。',
        category: 'shopping',
        publishTime: new Date(Date.now() - 30 * 60000),
        expiryDate: new Date(Date.now() + 2 * 24 * 60 * 60000),
        source: '京东',
        views: 1234,
        likes: 89,
        comments: 23,
        link: 'https://example.com'
      },
      {
        id: 2,
        title: '美团外卖新用户专享20元无门槛券',
        description: '新用户注册美团外卖即可获得20元无门槛优惠券，全场通用，有效期7天。',
        category: 'food',
        publishTime: new Date(Date.now() - 2 * 60 * 60000),
        expiryDate: new Date(Date.now() + 5 * 24 * 60 * 60000),
        source: '美团',
        views: 2156,
        likes: 156,
        comments: 45,
        link: 'https://example.com'
      },
      {
        id: 3,
        title: 'iPhone 15 Pro Max 官方降价1000元',
        description: 'Apple官方商店iPhone 15 Pro Max全系列降价1000元，支持24期免息分期。',
        category: 'digital',
        publishTime: new Date(Date.now() - 4 * 60 * 60000),
        expiryDate: new Date(Date.now() + 10 * 24 * 60 * 60000),
        source: 'Apple',
        views: 5678,
        likes: 234,
        comments: 67,
        link: 'https://example.com'
      },
      {
        id: 4,
        title: '支付宝扫码领取随机红包',
        description: '每天可扫码领取1-99元随机红包，线下支付时自动抵扣。',
        category: 'finance',
        publishTime: new Date(Date.now() - 6 * 60 * 60000),
        expiryDate: null,
        source: '支付宝',
        views: 3421,
        likes: 178,
        comments: 34,
        link: 'https://example.com'
      },
      {
        id: 5,
        title: '腾讯视频VIP会员3个月仅需19.9元',
        description: '限时特惠，腾讯视频VIP会员3个月套餐仅需19.9元，享受海量高清影视内容。',
        category: 'entertainment',
        publishTime: new Date(Date.now() - 8 * 60 * 60000),
        expiryDate: new Date(Date.now() + 3 * 24 * 60 * 60000),
        source: '腾讯视频',
        views: 1876,
        likes: 92,
        comments: 18,
        link: 'https://example.com'
      },
      {
        id: 6,
        title: '携程旅行酒店预订满300减100',
        description: '携程APP预订酒店满300元立减100元，全国酒店通用，周末不加价。',
        category: 'travel',
        publishTime: new Date(Date.now() - 12 * 60 * 60000),
        expiryDate: new Date(Date.now() + 7 * 24 * 60 * 60000),
        source: '携程',
        views: 987,
        likes: 45,
        comments: 12,
        link: 'https://example.com'
      }
    ]
    
    if (page === 1) {
      items.value = mockItems
    } else {
      items.value.push(...mockItems.map(item => ({ ...item, id: item.id + (page - 1) * 6 })))
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

// Watch for filter changes
watch([searchQuery, selectedCategory, sortBy], () => {
  // In a real app, you might want to refetch data here
})

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