<template>
  <header class="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
    <div class="max-w-6xl mx-auto px-4">
      <div class="flex items-center justify-between h-14">
        <!-- Logo和标题 -->
        <div class="flex items-center space-x-3">
          <NuxtLink to="/" class="flex items-center space-x-2 hover:opacity-80 transition-opacity">
            <div class="w-7 h-7 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <Icon name="heroicons:fire" class="w-4 h-4 text-white" />
            </div>
            <span class="text-lg font-bold text-gray-900 dark:text-white">
              热榜
            </span>
          </NuxtLink>
        </div>

        <!-- 右侧操作区 -->
        <div class="flex items-center space-x-3">
          <!-- 主题切换 -->
          <ThemeToggle />
          
          <!-- 用户认证状态 -->
          <div v-if="isAuthenticated" class="flex items-center space-x-2">
            <!-- 用户信息 -->
            <div class="flex items-center space-x-2 px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg">
              <Icon name="heroicons:user-circle" class="w-4 h-4 text-gray-600 dark:text-gray-300" />
              <span class="text-sm text-gray-700 dark:text-gray-300">{{ user?.username || user?.email }}</span>
            </div>
            
            <!-- 退出登录按钮 -->
            <button
              @click="handleLogout"
              class="p-2 text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
              title="退出登录"
            >
              <Icon name="heroicons:arrow-right-on-rectangle" class="w-4 h-4" />
            </button>
          </div>
          
          <!-- 未登录状态 -->
          <div v-else class="flex items-center space-x-2">
            <NuxtLink
              to="/login"
              class="px-3 py-1 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              登录
            </NuxtLink>
            <NuxtLink
              to="/register"
              class="px-3 py-1 text-sm bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              注册
            </NuxtLink>
          </div>
          
          <!-- 设置按钮 -->
          <button
            class="p-2 text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
            @click="toggleSettings"
          >
            <Icon name="heroicons:cog-6-tooth" class="w-4 h-4" />
          </button>
        </div>
      </div>

    </div>
    
    <!-- 设置面板 -->
    <Transition
      enter-active-class="transition-opacity duration-200"
      enter-from-class="opacity-0"
      enter-to-class="opacity-100"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="showSettings"
        class="absolute top-full right-0 mt-1 w-64 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50"
      >
        <div class="p-4">
          <h3 class="text-sm font-medium text-gray-900 dark:text-white mb-3">
            设置
          </h3>
          <div class="space-y-3">
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">字体大小</span>
              <select class="text-xs border border-gray-300 dark:border-gray-600 rounded px-2 py-1 bg-white dark:bg-gray-700">
                <option>小</option>
                <option selected>中</option>
                <option>大</option>
              </select>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-sm text-gray-700 dark:text-gray-300">偷摸模式</span>
              <button class="w-8 h-4 bg-gray-300 dark:bg-gray-600 rounded-full relative transition-colors">
                <div class="w-3 h-3 bg-white rounded-full absolute top-0.5 left-0.5 transition-transform"></div>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </header>
</template>

<script setup lang="ts">
import { useNotification } from '~/composables/useNotification'

// 认证相关
const { user, isAuthenticated, logout } = useAuth()
const notification = useNotification()

// 响应式数据
const showSettings = ref(false)

// 方法
const toggleSettings = () => {
  showSettings.value = !showSettings.value
}

// 处理退出登录
const handleLogout = async () => {
  try {
    await logout()
    notification.success('退出登录成功')
  } catch (error) {
    notification.error('退出登录失败', '请稍后重试')
  }
}

// 点击外部关闭设置面板
const handleClickOutside = (event: Event) => {
  const target = event.target as Element
  if (!target.closest('.settings-panel') && !target.closest('[data-settings-trigger]')) {
    showSettings.value = false
  }
}

// 生命周期
onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.nav-link {
  @apply flex items-center px-3 py-2 text-sm font-medium transition-colors duration-200;
}

.nav-link:hover {
  @apply text-gray-900 dark:text-white;
}
</style>