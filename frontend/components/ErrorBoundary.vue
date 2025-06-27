<template>
  <div class="error-boundary">
    <!-- 正常状态 -->
    <template v-if="!hasError">
      <slot></slot>
    </template>

    <!-- 错误状态 -->
    <template v-else>
      <div class="error-boundary__container">
        <!-- 自定义错误内容 -->
        <slot name="error" :error="error" :retry="retry" :reset="reset">
          <!-- 默认错误显示 -->
          <div class="error-boundary__content">
            <!-- 错误图标 -->
            <div class="error-boundary__icon">
              <Icon 
                name="heroicons:exclamation-triangle" 
                class="w-16 h-16 text-red-500"
              />
            </div>

            <!-- 错误标题 -->
            <h2 class="error-boundary__title">
              {{ errorTitle }}
            </h2>

            <!-- 错误描述 -->
            <p class="error-boundary__description">
              {{ errorDescription }}
            </p>

            <!-- 错误详情（开发模式） -->
            <details v-if="showDetails && error" class="error-boundary__details">
              <summary class="error-boundary__details-summary">
                查看错误详情
              </summary>
              <div class="error-boundary__details-content">
                <pre class="error-boundary__error-message">{{ error.message }}</pre>
                <pre v-if="error.stack" class="error-boundary__error-stack">{{ error.stack }}</pre>
              </div>
            </details>

            <!-- 操作按钮 -->
            <div class="error-boundary__actions">
              <UButton
                label="重试"
                icon="heroicons:arrow-path"
                color="primary"
                size="lg"
                :loading="retrying"
                @click="handleRetry"
              />
              
              <UButton
                label="重置"
                icon="heroicons:arrow-uturn-left"
                color="gray"
                variant="ghost"
                size="lg"
                @click="handleReset"
              />
              
              <UButton
                v-if="showReportButton"
                label="报告问题"
                icon="heroicons:bug-ant"
                color="red"
                variant="outline"
                size="lg"
                @click="handleReport"
              />
            </div>

            <!-- 建议操作 -->
            <div v-if="suggestions.length > 0" class="error-boundary__suggestions">
              <h3 class="error-boundary__suggestions-title">您可以尝试：</h3>
              <ul class="error-boundary__suggestions-list">
                <li 
                  v-for="(suggestion, index) in suggestions" 
                  :key="index"
                  class="error-boundary__suggestion-item"
                >
                  {{ suggestion }}
                </li>
              </ul>
            </div>
          </div>
        </slot>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
interface Props {
  fallback?: string
  showDetails?: boolean
  showReportButton?: boolean
  maxRetries?: number
  retryDelay?: number
  onError?: (error: Error, errorInfo: any) => void
  onRetry?: () => void | Promise<void>
  onReset?: () => void
  onReport?: (error: Error) => void
}

interface Emits {
  'error': [error: Error, errorInfo: any]
  'retry': []
  'reset': []
  'report': [error: Error]
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: process.dev,
  showReportButton: true,
  maxRetries: 3,
  retryDelay: 1000
})

const emit = defineEmits<Emits>()

// 使用组合式函数
const { error: notifyError, success } = useNotification()

// 响应式数据
const hasError = ref(false)
const error = ref<Error | null>(null)
const errorInfo = ref<any>(null)
const retryCount = ref(0)
const retrying = ref(false)

// 计算属性
const errorTitle = computed(() => {
  if (!error.value) return '出现错误'
  
  // 根据错误类型返回不同标题
  if (error.value.name === 'ChunkLoadError') {
    return '资源加载失败'
  }
  
  if (error.value.name === 'NetworkError') {
    return '网络连接错误'
  }
  
  if (error.value.name === 'TypeError') {
    return '类型错误'
  }
  
  if (error.value.name === 'ReferenceError') {
    return '引用错误'
  }
  
  return '应用程序错误'
})

const errorDescription = computed(() => {
  if (!error.value) return '应用程序遇到了意外错误'
  
  // 根据错误类型返回不同描述
  if (error.value.name === 'ChunkLoadError') {
    return '页面资源加载失败，这可能是由于网络问题或服务器更新导致的。'
  }
  
  if (error.value.name === 'NetworkError') {
    return '无法连接到服务器，请检查您的网络连接。'
  }
  
  if (error.value.message.includes('fetch')) {
    return '数据获取失败，请检查网络连接或稍后重试。'
  }
  
  return '应用程序遇到了意外错误，我们正在努力解决这个问题。'
})

const suggestions = computed(() => {
  const suggestions: string[] = []
  
  if (!error.value) return suggestions
  
  // 根据错误类型提供建议
  if (error.value.name === 'ChunkLoadError') {
    suggestions.push('刷新页面重新加载资源')
    suggestions.push('清除浏览器缓存')
    suggestions.push('检查网络连接')
  } else if (error.value.name === 'NetworkError') {
    suggestions.push('检查网络连接')
    suggestions.push('稍后重试')
    suggestions.push('联系技术支持')
  } else {
    suggestions.push('刷新页面')
    suggestions.push('清除浏览器缓存')
    suggestions.push('使用其他浏览器')
  }
  
  return suggestions
})

// 错误处理
const captureError = (err: Error, info: any) => {
  hasError.value = true
  error.value = err
  errorInfo.value = info
  retryCount.value = 0
  
  // 调用错误回调
  if (props.onError) {
    props.onError(err, info)
  }
  
  // 发出错误事件
  emit('error', err, info)
  
  // 记录错误到控制台
  console.error('ErrorBoundary caught an error:', err)
  console.error('Error info:', info)
  
  // 发送错误报告（如果配置了）
  if (process.client) {
    reportError(err, info)
  }
}

// 重试逻辑
const retry = async () => {
  if (retryCount.value >= props.maxRetries) {
    notifyError('重试失败', `已达到最大重试次数 (${props.maxRetries})`)
    return
  }
  
  retrying.value = true
  retryCount.value++
  
  try {
    // 延迟重试
    await new Promise(resolve => setTimeout(resolve, props.retryDelay))
    
    // 调用重试回调
    if (props.onRetry) {
      await props.onRetry()
    }
    
    // 重置错误状态
    hasError.value = false
    error.value = null
    errorInfo.value = null
    
    success('重试成功', '应用程序已恢复正常')
    
    emit('retry')
  } catch (err) {
    console.error('Retry failed:', err)
    notifyError('重试失败', '请稍后再试')
  } finally {
    retrying.value = false
  }
}

// 重置逻辑
const reset = () => {
  hasError.value = false
  error.value = null
  errorInfo.value = null
  retryCount.value = 0
  retrying.value = false
  
  if (props.onReset) {
    props.onReset()
  }
  
  emit('reset')
}

// 报告错误
const reportError = async (err: Error, info: any) => {
  try {
    // 这里可以集成错误报告服务，如 Sentry
    const errorReport = {
      message: err.message,
      stack: err.stack,
      name: err.name,
      url: window.location.href,
      userAgent: navigator.userAgent,
      timestamp: new Date().toISOString(),
      errorInfo: info
    }
    
    // 发送到错误报告服务
    // await $fetch('/api/error-report', {
    //   method: 'POST',
    //   body: errorReport
    // })
    
    console.log('Error report:', errorReport)
  } catch (reportErr) {
    console.error('Failed to report error:', reportErr)
  }
}

// 事件处理
const handleRetry = () => {
  retry()
}

const handleReset = () => {
  reset()
}

const handleReport = () => {
  if (error.value && props.onReport) {
    props.onReport(error.value)
  }
  
  if (error.value) {
    emit('report', error.value)
  }
  
  success('问题已报告', '感谢您的反馈，我们会尽快处理')
}

// 全局错误处理
if (process.client) {
  // 捕获未处理的 Promise 拒绝
  window.addEventListener('unhandledrejection', (event) => {
    captureError(new Error(event.reason), { type: 'unhandledrejection' })
  })
  
  // 捕获全局错误
  window.addEventListener('error', (event) => {
    captureError(event.error || new Error(event.message), { 
      type: 'error',
      filename: event.filename,
      lineno: event.lineno,
      colno: event.colno
    })
  })
}

// Vue 错误处理
const errorHandler = (err: unknown, instance: any, info: string) => {
  const error = err instanceof Error ? err : new Error(String(err))
  captureError(error, { instance, info, type: 'vue' })
}

// 注册 Vue 错误处理器
if (process.client) {
  const app = getCurrentInstance()?.appContext.app
  if (app) {
    app.config.errorHandler = errorHandler
  }
}

// 暴露方法
defineExpose({
  captureError,
  retry,
  reset,
  hasError: readonly(hasError),
  error: readonly(error)
})
</script>

<style scoped>
.error-boundary {
  @apply w-full;
}

.error-boundary__container {
  @apply min-h-[400px] flex items-center justify-center;
  @apply bg-gray-50 dark:bg-gray-900;
  @apply rounded-lg border border-gray-200 dark:border-gray-700;
}

.error-boundary__content {
  @apply max-w-md mx-auto text-center p-8;
}

.error-boundary__icon {
  @apply mb-6;
}

.error-boundary__title {
  @apply text-2xl font-bold text-gray-900 dark:text-white mb-4;
}

.error-boundary__description {
  @apply text-gray-600 dark:text-gray-400 mb-6 leading-relaxed;
}

.error-boundary__details {
  @apply text-left mb-6 bg-gray-100 dark:bg-gray-800 rounded-lg p-4;
}

.error-boundary__details-summary {
  @apply cursor-pointer text-sm font-medium text-gray-700 dark:text-gray-300;
  @apply hover:text-gray-900 dark:hover:text-white;
}

.error-boundary__details-content {
  @apply mt-3 space-y-2;
}

.error-boundary__error-message {
  @apply text-xs text-red-600 dark:text-red-400;
  @apply bg-red-50 dark:bg-red-900/20 p-2 rounded;
  @apply overflow-x-auto;
}

.error-boundary__error-stack {
  @apply text-xs text-gray-600 dark:text-gray-400;
  @apply bg-gray-50 dark:bg-gray-800 p-2 rounded;
  @apply overflow-x-auto max-h-32;
}

.error-boundary__actions {
  @apply flex flex-col sm:flex-row items-center justify-center;
  @apply space-y-2 sm:space-y-0 sm:space-x-3 mb-6;
}

.error-boundary__suggestions {
  @apply text-left;
}

.error-boundary__suggestions-title {
  @apply text-sm font-medium text-gray-900 dark:text-white mb-2;
}

.error-boundary__suggestions-list {
  @apply space-y-1;
}

.error-boundary__suggestion-item {
  @apply text-sm text-gray-600 dark:text-gray-400;
  @apply flex items-start;
}

.error-boundary__suggestion-item::before {
  content: '•';
  @apply text-gray-400 mr-2 flex-shrink-0;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .error-boundary__content {
    @apply p-6;
  }
  
  .error-boundary__title {
    @apply text-xl;
  }
  
  .error-boundary__actions {
    @apply flex-col space-y-2 space-x-0;
  }
}

/* 动画效果 */
.error-boundary__container {
  animation: fadeIn 0.3s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .error-boundary__container {
    animation: none;
  }
}
</style>