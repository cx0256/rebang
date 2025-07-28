<template>
  <div class="hot-list-manager">
    <!-- 控制面板 -->
    <div class="control-panel mb-6">
      <div class="flex flex-wrap gap-4 items-center">
        <button 
          @click="refreshAllData" 
          :disabled="loading"
          class="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50"
        >
          <Icon name="mdi:refresh" class="mr-2" />
          {{ loading ? '刷新中...' : '刷新数据' }}
        </button>
        
        <button 
          @click="triggerCrawl" 
          :disabled="crawling"
          class="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 disabled:opacity-50"
        >
          <Icon name="mdi:spider" class="mr-2" />
          {{ crawling ? '爬取中...' : '手动爬取' }}
        </button>
        
        <select 
          v-model="selectedPlatform" 
          @change="filterByPlatform"
          class="px-3 py-2 border rounded"
        >
          <option value="">所有平台</option>
          <option v-for="platform in platforms" :key="platform" :value="platform">
            {{ platform }}
          </option>
        </select>
        
        <span class="text-sm text-gray-500">
          最后更新: {{ lastUpdateTime }}
        </span>
      </div>
    </div>

    <!-- 热榜数据展示 -->
    <div class="hot-lists-grid">
      <div 
        v-for="(list, platform) in filteredHotLists" 
        :key="platform"
        class="hot-list-card bg-white rounded-lg shadow-md p-6"
      >
        <div class="flex items-center justify-between mb-4">
          <h3 class="text-xl font-bold text-gray-800">
            {{ platform }}
          </h3>
          <div class="flex items-center space-x-2">
            <span class="text-sm text-gray-500">
              {{ list.length }} 条
            </span>
            <button 
               @click="refreshPlatformData(platform)" 
               :disabled="refreshingPlatforms[platform]"
               class="p-2 rounded-full text-gray-500 hover:text-blue-500 hover:bg-blue-50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
               :title="refreshingPlatforms[platform] ? '刷新中...' : `刷新${platform}数据`"
             >
               <Icon 
                 name="mdi:refresh" 
                 :class="{ 
                   'animate-spin text-blue-500': refreshingPlatforms[platform],
                   'hover:scale-110': !refreshingPlatforms[platform]
                 }" 
                 class="transition-transform duration-200"
               />
             </button>
          </div>
        </div>
        
        <div class="hot-items-container h-96 overflow-y-auto border border-gray-200 rounded-lg bg-gray-50">
          <div 
            v-for="(item, index) in list.slice(0, 30)" 
            :key="item.id || index"
            class="hot-item flex items-start space-x-3 p-3 hover:bg-gray-50 rounded transition-colors duration-200"
          >
            <span class="rank-number flex-shrink-0 w-6 h-6 bg-red-500 text-white text-xs rounded-full flex items-center justify-center">
              {{ item.rank || index + 1 }}
            </span>
            
            <div class="flex-1 min-w-0">
              <a 
                :href="item.url" 
                target="_blank" 
                class="block text-sm font-medium text-gray-900 hover:text-blue-600 line-clamp-2"
                :title="item.title"
              >
                {{ item.title }}
              </a>
              
              <div class="flex items-center flex-wrap gap-3 mt-1 text-xs text-gray-500">
                <span v-if="item.hot_value" class="flex items-center bg-red-100 text-red-600 px-2 py-1 rounded-full">
                  <Icon name="mdi:fire" class="mr-1" />
                  {{ item.hot_value }}
                </span>
                
                <span v-if="item.author" class="flex items-center">
                  <Icon name="mdi:account" class="mr-1" />
                  {{ item.author }}
                </span>
                
                <span v-if="item.comment_count" class="flex items-center">
                  <Icon name="mdi:comment" class="mr-1" />
                  {{ item.comment_count }}
                </span>
                
                <span v-if="item.crawled_at" class="flex items-center">
                  <Icon name="mdi:clock" class="mr-1" />
                  {{ formatTime(item.crawled_at) }}
                </span>
                
                <span v-if="item.tags && item.tags.length > 0" class="flex items-center">
                  <Icon name="mdi:tag" class="mr-1" />
                  {{ item.tags.join(', ') }}
                </span>
              </div>
              
              <p v-if="item.summary" class="text-xs text-gray-600 mt-2 line-clamp-2">
                {{ item.summary }}
              </p>
            </div>
            
            <!-- 图片展示 -->
            <div v-if="item.image_url" class="flex-shrink-0 ml-3">
              <img 
                :src="item.image_url" 
                :alt="item.title"
                class="w-16 h-16 object-cover rounded"
                loading="lazy"
                @error="$event.target.style.display='none'"
              />
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-if="Object.keys(filteredHotLists).length === 0" class="text-center py-12">
      <Icon name="mdi:database-off" class="text-6xl text-gray-300 mb-4" />
      <p class="text-gray-500">暂无热榜数据</p>
      <button 
        @click="triggerCrawl" 
        class="mt-4 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        开始爬取数据
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'

// 响应式数据
const hotLists = ref({})
const platforms = ref([])
const selectedPlatform = ref('')
const loading = ref(false)
const crawling = ref(false)
const lastUpdateTime = ref('')
const refreshInterval = ref(null)
const refreshingPlatforms = ref({})

// 计算属性
const filteredHotLists = computed(() => {
  if (!selectedPlatform.value) {
    return hotLists.value
  }
  
  const filtered = {}
  if (hotLists.value[selectedPlatform.value]) {
    filtered[selectedPlatform.value] = hotLists.value[selectedPlatform.value]
  }
  return filtered
})

// 方法
const fetchHotLists = async () => {
  try {
    loading.value = true
    
    const response = await $fetch('/api/v1/hot')
    
    if (response.success && response.data && response.data.hot_lists) {
      // 按平台分组数据
      const groupedData = {}
      
      response.data.hot_lists.forEach(platformData => {
        const platformName = platformData.display_name || platformData.name || '未知平台'
        groupedData[platformName] = platformData.items || []
      })
      
      hotLists.value = groupedData
      platforms.value = Object.keys(groupedData)
      lastUpdateTime.value = response.data.last_updated ? 
        new Date(response.data.last_updated).toLocaleString() : 
        new Date().toLocaleString()
    }
  } catch (error) {
    console.error('获取热榜数据失败:', error)
    // 这里可以添加错误提示
  } finally {
    loading.value = false
  }
}

const triggerCrawl = async () => {
  try {
    crawling.value = true
    
    const response = await $fetch('/api/v1/crawlers/crawl/all', {
      method: 'POST'
    })
    
    if (response.success) {
      // 等待一段时间后刷新数据
      setTimeout(() => {
        fetchHotLists()
      }, 5000)
    }
  } catch (error) {
    console.error('触发爬取失败:', error)
  } finally {
    crawling.value = false
  }
}

const refreshAllData = () => {
  fetchHotLists()
}

const filterByPlatform = () => {
  // 过滤逻辑已在计算属性中处理
}

// 刷新单个平台数据
const refreshPlatformData = async (platformDisplayName) => {
  try {
    // 设置刷新状态
    refreshingPlatforms.value[platformDisplayName] = true
    
    // 将显示名称转换为API名称（小写，去除特殊字符）
    const platformApiName = platformDisplayName.toLowerCase().replace(/[^a-z0-9]/g, '')
    
    // 根据平台名称映射到正确的API端点
    const platformNameMap = {
      '知乎': 'zhihu',
      '虎扑': 'hupu',
      'IT之家': 'ithome',
      '微博': 'weibo',
      '今日头条': 'toutiao',
      'B站': 'bilibili',
      'NGA': 'nga',
      '什么值得买': 'smzdm',
      '36氪': 'kr36',
      'ZOL': 'zol'
    }
    
    const apiName = platformNameMap[platformDisplayName] || platformApiName
    
    const response = await $fetch(`/api/v1/hot/${apiName}`)
    
    if (response.success && response.data) {
      // 提取热榜数据
      let items = []
      if (response.data.categories && response.data.categories.length > 0) {
        items = response.data.categories.flatMap(cat => cat.items || [])
      }
      
      // 更新对应平台的数据
      hotLists.value[platformDisplayName] = items
      
      // 更新最后更新时间
      lastUpdateTime.value = new Date().toLocaleString()
    }
  } catch (error) {
    console.error(`刷新${platformDisplayName}数据失败:`, error)
    // 这里可以添加错误提示
  } finally {
    // 清除刷新状态
    refreshingPlatforms.value[platformDisplayName] = false
  }
}

const formatTime = (timeString) => {
  if (!timeString) return ''
  
  const date = new Date(timeString)
  const now = new Date()
  const diff = now - date
  
  if (diff < 60000) { // 1分钟内
    return '刚刚'
  } else if (diff < 3600000) { // 1小时内
    return `${Math.floor(diff / 60000)}分钟前`
  } else if (diff < 86400000) { // 24小时内
    return `${Math.floor(diff / 3600000)}小时前`
  } else {
    return date.toLocaleDateString()
  }
}

// 生命周期
onMounted(() => {
  fetchHotLists()
  
  // 设置自动刷新（每5分钟）
  refreshInterval.value = setInterval(() => {
    fetchHotLists()
  }, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (refreshInterval.value) {
    clearInterval(refreshInterval.value)
  }
})
</script>

<style scoped>
.hot-list-manager {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.hot-lists-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(450px, 1fr));
  gap: 24px;
}

.hot-list-card {
  border: 1px solid #e5e7eb;
  transition: all 0.3s ease;
  height: fit-content;
  max-height: 600px;
  display: flex;
  flex-direction: column;
}

.hot-list-card:hover {
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.hot-items-container {
  flex: 1;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
  max-height: 500px;
}

.hot-items-container::-webkit-scrollbar {
  width: 6px;
}

.hot-items-container::-webkit-scrollbar-track {
  background: #f7fafc;
  border-radius: 3px;
}

.hot-items-container::-webkit-scrollbar-thumb {
  background: #cbd5e0;
  border-radius: 3px;
  transition: background 0.2s;
}

.hot-items-container::-webkit-scrollbar-thumb:hover {
  background: #a0aec0;
}

.hot-item {
  transition: all 0.2s ease;
  border-bottom: 1px solid #f7fafc;
}

.hot-item:last-child {
  border-bottom: none;
}

.hot-item:hover {
  background-color: #f8fafc;
  transform: translateX(4px);
}

.rank-number {
  font-weight: bold;
  transition: all 0.2s ease;
}

.hot-item:hover .rank-number {
  transform: scale(1.1);
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .hot-lists-grid {
    grid-template-columns: repeat(auto-fit, minmax(380px, 1fr));
    gap: 16px;
  }
}

@media (max-width: 768px) {
  .hot-list-manager {
    padding: 16px;
  }
  
  .hot-lists-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .hot-list-card {
    max-height: 400px;
  }
  
  .hot-items-container {
    max-height: 320px;
  }
  
  .control-panel .flex {
    flex-direction: column;
    align-items: stretch;
    gap: 12px;
  }
  
  .control-panel button,
  .control-panel select {
    width: 100%;
  }
  
  .hot-item {
    padding: 12px;
  }
  
  .hot-item:hover {
    transform: none;
  }
}

@media (max-width: 480px) {
  .hot-list-manager {
    padding: 12px;
  }
  
  .hot-list-card {
    padding: 16px;
    max-height: 350px;
  }
  
  .hot-items-container {
    max-height: 270px;
  }
  
  .hot-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
  
  .hot-item img {
    width: 100%;
    height: 120px;
    margin: 8px 0 0 0;
  }
}
</style>