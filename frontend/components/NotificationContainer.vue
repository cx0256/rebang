<template>
  <Teleport to="body">
    <!-- 通知容器 -->
    <div class="fixed top-4 right-4 z-50 space-y-2 max-w-sm w-full">
      <TransitionGroup
        name="notification"
        tag="div"
        class="space-y-2"
      >
        <div
          v-for="notification in notifications"
          :key="notification.id"
          class="notification-card"
          :class="getNotificationClass(notification.type)"
          @click="removeNotification(notification.id)"
        >
          <!-- 图标 -->
          <div class="flex-shrink-0">
            <Icon
              :name="getNotificationIcon(notification.type)"
              class="w-5 h-5"
              :class="getIconClass(notification.type)"
            />
          </div>

          <!-- 内容 -->
          <div class="flex-1 min-w-0">
            <h4 v-if="notification.title" class="text-sm font-medium truncate">
              {{ notification.title }}
            </h4>
            <p class="text-sm opacity-90 mt-1">
              {{ notification.message }}
            </p>
          </div>

          <!-- 关闭按钮 -->
          <button
            class="flex-shrink-0 ml-2 p-1 rounded-full hover:bg-black/10 transition-colors"
            @click.stop="removeNotification(notification.id)"
          >
            <Icon name="heroicons:x-mark" class="w-4 h-4" />
          </button>

          <!-- 进度条 -->
          <div
            v-if="notification.duration && notification.duration > 0"
            class="absolute bottom-0 left-0 h-1 bg-current opacity-30 transition-all duration-100 ease-linear"
            :style="{ width: getProgressWidth(notification) }"
          />
        </div>
      </TransitionGroup>
    </div>

    <!-- 确认对话框 -->
    <UModal v-model="showConfirmDialog" :ui="{ width: 'max-w-md' }">
      <div class="p-6">
        <div class="flex items-start space-x-3">
          <div class="flex-shrink-0">
            <Icon
              :name="confirmDialog.icon || 'heroicons:question-mark-circle'"
              class="w-6 h-6 text-amber-500"
            />
          </div>
          <div class="flex-1">
            <h3 class="text-lg font-medium text-gray-900 dark:text-white">
              {{ confirmDialog.title || '确认操作' }}
            </h3>
            <p class="mt-2 text-sm text-gray-600 dark:text-gray-400">
              {{ confirmDialog.message }}
            </p>
          </div>
        </div>
        <div class="flex justify-end space-x-3 mt-6">
          <UButton
            variant="outline"
            @click="handleConfirmCancel"
          >
            {{ confirmDialog.cancelText || '取消' }}
          </UButton>
          <UButton
            :color="(confirmDialog.type === 'danger' ? 'red' : 'primary') as any"
            @click="handleConfirmOk"
          >
            {{ confirmDialog.confirmText || '确认' }}
          </UButton>
        </div>
      </div>
    </UModal>

    <!-- 加载对话框 -->
    <UModal v-model="showLoadingDialog" :ui="{ width: 'max-w-sm' }" :closable="false">
      <div class="p-6 text-center">
        <div class="flex justify-center mb-4">
          <Icon name="heroicons:arrow-path" class="w-8 h-8 text-blue-500 animate-spin" />
        </div>
        <h3 class="text-lg font-medium text-gray-900 dark:text-white mb-2">
          {{ loadingDialog.title || '加载中' }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          {{ loadingDialog.message || '请稍候...' }}
        </p>
        <div v-if="loadingDialog.progress !== undefined" class="mt-4">
          <div class="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              class="bg-blue-500 h-2 rounded-full transition-all duration-300"
              :style="{ width: `${loadingDialog.progress}%` }"
            />
          </div>
          <p class="text-xs text-gray-500 mt-1">
            {{ Math.round(loadingDialog.progress) }}%
          </p>
        </div>
      </div>
    </UModal>
  </Teleport>
</template>

<script setup lang="ts">
import type { Notification } from '~/types'

// 使用通知组合式函数
const {
  notifications,
  removeNotification
} = useNotification()

// 确认对话框状态
const showConfirmDialog = ref(false)
const confirmDialog = ref({
  title: '',
  message: '',
  icon: '',
  type: 'info' as 'info' | 'danger',
  cancelText: '取消',
  confirmText: '确认'
})

// 加载对话框状态
const showLoadingDialog = ref(false)
const loadingDialog = ref({
  title: '',
  message: '',
  progress: 0
})

// 对话框处理方法
const handleConfirmOk = () => {
  showConfirmDialog.value = false
}

const handleConfirmCancel = () => {
  showConfirmDialog.value = false
}

// 获取通知样式类
const getNotificationClass = (type: Notification['type']) => {
  const baseClass = 'notification-card'
  const typeClasses = {
    success: 'bg-green-500 text-white',
    error: 'bg-red-500 text-white',
    warning: 'bg-amber-500 text-white',
    info: 'bg-blue-500 text-white'
  }
  return `${baseClass} ${typeClasses[type]}`
}

// 获取通知图标
const getNotificationIcon = (type: Notification['type']) => {
  const icons = {
    success: 'heroicons:check-circle',
    error: 'heroicons:x-circle',
    warning: 'heroicons:exclamation-triangle',
    info: 'heroicons:information-circle'
  }
  return icons[type]
}

// 获取图标样式类
const getIconClass = (type: Notification['type']) => {
  return 'text-current'
}

// 获取进度条宽度
const getProgressWidth = (notification: Notification) => {
  if (!notification.duration || !notification.createdAt) return '0%'
  
  const elapsed = Date.now() - notification.createdAt
  const progress = Math.max(0, 100 - (elapsed / notification.duration) * 100)
  return `${progress}%`
}

// 定时更新进度条
let progressInterval: NodeJS.Timeout | null = null

const startProgressUpdate = () => {
  if (progressInterval) clearInterval(progressInterval)
  
  progressInterval = setInterval(() => {
    // 触发响应式更新
    nextTick()
  }, 100)
}

const stopProgressUpdate = () => {
  if (progressInterval) {
    clearInterval(progressInterval)
    progressInterval = null
  }
}

// 监听通知变化
watch(
  notifications,
  (newNotifications) => {
    const hasTimedNotifications = newNotifications.some(
      n => n.duration && n.duration > 0
    )
    
    if (hasTimedNotifications) {
      startProgressUpdate()
    } else {
      stopProgressUpdate()
    }
  },
  { immediate: true }
)

// 组件卸载时清理定时器
onUnmounted(() => {
  stopProgressUpdate()
})
</script>

<style scoped>
.notification-card {
  @apply relative flex items-start space-x-3 p-4 rounded-lg shadow-lg cursor-pointer;
  @apply transform transition-all duration-300 ease-out;
  @apply hover:scale-105 hover:shadow-xl;
}

/* 通知动画 */
.notification-enter-active {
  transition: all 0.3s ease-out;
}

.notification-leave-active {
  transition: all 0.3s ease-in;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%) scale(0.8);
}

.notification-move {
  transition: transform 0.3s ease;
}
</style>