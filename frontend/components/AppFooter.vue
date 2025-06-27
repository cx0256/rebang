<template>
  <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-16">
    <div class="container-responsive py-12">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-8">
        <!-- 品牌信息 -->
        <div class="col-span-1 md:col-span-2">
          <div class="flex items-center space-x-2 mb-4">
            <div class="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Icon name="heroicons:fire" class="w-5 h-5 text-white" />
            </div>
            <span class="text-xl font-bold text-gray-900 dark:text-white">
              热榜
            </span>
          </div>
          <p class="text-gray-600 dark:text-gray-400 mb-4 max-w-md">
            聚合各大平台热门内容，让你一站式了解全网热点。支持知乎、微博、GitHub、B站、豆瓣等多个平台。
          </p>
          <div class="flex space-x-4">
            <a
              v-for="social in socialLinks"
              :key="social.name"
              :href="social.url"
              target="_blank"
              rel="noopener noreferrer"
              class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              :title="social.name"
            >
              <Icon :name="social.icon" class="w-5 h-5" />
            </a>
          </div>
        </div>

        <!-- 快速链接 -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
            快速链接
          </h3>
          <ul class="space-y-2">
            <li v-for="link in quickLinks" :key="link.path">
              <NuxtLink
                :to="link.path"
                class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
              >
                {{ link.label }}
              </NuxtLink>
            </li>
          </ul>
        </div>

        <!-- 支持的平台 -->
        <div>
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white uppercase tracking-wider mb-4">
            支持平台
          </h3>
          <ul class="space-y-2">
            <li v-for="platform in supportedPlatforms" :key="platform.name">
              <a
                :href="platform.url"
                target="_blank"
                rel="noopener noreferrer"
                class="text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors flex items-center"
              >
                <Icon :name="platform.icon" class="w-4 h-4 mr-2" />
                {{ platform.name }}
              </a>
            </li>
          </ul>
        </div>
      </div>

      <!-- 分割线 -->
      <div class="border-t border-gray-200 dark:border-gray-700 mt-8 pt-8">
        <div class="flex flex-col md:flex-row justify-between items-center space-y-4 md:space-y-0">
          <!-- 版权信息 -->
          <div class="text-sm text-gray-600 dark:text-gray-400">
            <p>
              © {{ currentYear }} 热榜. All rights reserved.
            </p>
          </div>

          <!-- 法律链接 -->
          <div class="flex space-x-6">
            <NuxtLink
              v-for="legal in legalLinks"
              :key="legal.path"
              :to="legal.path"
              class="text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              {{ legal.label }}
            </NuxtLink>
          </div>

          <!-- 统计信息 -->
          <div v-if="stats" class="text-sm text-gray-600 dark:text-gray-400">
            <span>今日更新 {{ stats.today_updates }} 条</span>
          </div>
        </div>
      </div>

      <!-- 备案信息 -->
      <div class="text-center mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p class="text-xs text-gray-500 dark:text-gray-500">
          本站仅聚合展示各平台公开内容，不存储任何用户数据
        </p>
      </div>
    </div>
  </footer>
</template>

<script setup lang="ts">
import type { Statistics } from '~/types'

// 使用组合式函数
const { fetchStatistics } = useHotList()

// 响应式数据
const stats = ref<Statistics | null>(null)

// 当前年份
const currentYear = new Date().getFullYear()

// 社交媒体链接
const socialLinks = [
  {
    name: 'GitHub',
    url: 'https://github.com/momoyu-hot',
    icon: 'simple-icons:github'
  },
  {
    name: 'Twitter',
    url: 'https://twitter.com/momoyu_hot',
    icon: 'simple-icons:twitter'
  },
  {
    name: 'Telegram',
    url: 'https://t.me/momoyu_hot',
    icon: 'simple-icons:telegram'
  },
  {
    name: 'RSS',
    url: '/api/rss',
    icon: 'heroicons:rss'
  }
]

// 快速链接
const quickLinks = [
  { label: '首页', path: '/' },
  { label: '所有平台', path: '/platforms' },
  { label: '趋势分析', path: '/trending' },
  { label: '收藏夹', path: '/favorites' },
  { label: 'API文档', path: '/docs' },
  { label: '反馈建议', path: '/feedback' }
]

// 支持的平台
const supportedPlatforms = [
  {
    name: '知乎',
    url: 'https://zhihu.com',
    icon: 'simple-icons:zhihu'
  },
  {
    name: '微博',
    url: 'https://weibo.com',
    icon: 'simple-icons:sinaweibo'
  },
  {
    name: 'GitHub',
    url: 'https://github.com',
    icon: 'simple-icons:github'
  },
  {
    name: 'B站',
    url: 'https://bilibili.com',
    icon: 'simple-icons:bilibili'
  },
  {
    name: '豆瓣',
    url: 'https://douban.com',
    icon: 'simple-icons:douban'
  },
  {
    name: '掘金',
    url: 'https://juejin.cn',
    icon: 'simple-icons:juejin'
  }
]

// 法律链接
const legalLinks = [
  { label: '隐私政策', path: '/privacy' },
  { label: '服务条款', path: '/terms' },
  { label: '免责声明', path: '/disclaimer' },
  { label: '联系我们', path: '/contact' }
]

// 获取统计数据
const loadStats = async () => {
  try {
    const data = await fetchStatistics()
    if (data) {
      stats.value = data
    }
  } catch (error) {
    console.error('Failed to load footer stats:', error)
  }
}

// 页面挂载时加载数据
onMounted(() => {
  loadStats()
})
</script>

<style scoped>
/* Footer特定样式 */
</style>