<template>
  <Transition
    enter-active-class="transition-all duration-300 ease-out"
    enter-from-class="opacity-0 scale-75 translate-y-4"
    enter-to-class="opacity-100 scale-100 translate-y-0"
    leave-active-class="transition-all duration-200 ease-in"
    leave-from-class="opacity-100 scale-100 translate-y-0"
    leave-to-class="opacity-0 scale-75 translate-y-4"
  >
    <button
      v-show="isVisible"
      class="back-to-top-btn"
      :class="{
        'back-to-top-btn--extended': showProgress
      }"
      @click="scrollToTop"
      @mouseenter="handleMouseEnter"
      @mouseleave="handleMouseLeave"
    >
      <!-- 进度环 -->
      <div v-if="showProgress" class="absolute inset-0">
        <svg class="w-full h-full transform -rotate-90" viewBox="0 0 36 36">
          <path
            class="text-gray-300 dark:text-gray-600"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
          <path
            class="text-blue-500 transition-all duration-300 ease-out"
            stroke="currentColor"
            stroke-width="2"
            fill="none"
            stroke-linecap="round"
            :stroke-dasharray="circumference"
            :stroke-dashoffset="strokeDashoffset"
            d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
          />
        </svg>
      </div>

      <!-- 图标 -->
      <div class="relative z-10 flex items-center justify-center">
        <Icon
          name="heroicons:arrow-up"
          class="w-5 h-5 text-white transition-transform duration-200"
          :class="{
            'transform -translate-y-0.5': isHovered
          }"
        />
      </div>

      <!-- 提示文本 -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 scale-90"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-90"
      >
        <div
          v-if="isHovered && showTooltip"
          class="absolute right-full mr-3 px-2 py-1 bg-gray-900 dark:bg-gray-700 text-white text-xs rounded whitespace-nowrap"
        >
          回到顶部
          <div class="absolute top-1/2 left-full transform -translate-y-1/2 border-l-4 border-l-gray-900 dark:border-l-gray-700 border-y-4 border-y-transparent" />
        </div>
      </Transition>
    </button>
  </Transition>
</template>

<script setup lang="ts">
interface Props {
  // 显示阈值（滚动距离）
  threshold?: number
  // 是否显示滚动进度
  showProgress?: boolean
  // 是否显示提示文本
  showTooltip?: boolean
  // 滚动动画持续时间
  duration?: number
  // 滚动行为
  behavior?: 'smooth' | 'auto'
}

const props = withDefaults(defineProps<Props>(), {
  threshold: 300,
  showProgress: true,
  showTooltip: true,
  duration: 800,
  behavior: 'smooth'
})

// 响应式数据
const isVisible = ref(false)
const isHovered = ref(false)
const scrollProgress = ref(0)

// 计算属性
const circumference = computed(() => 2 * Math.PI * 15.9155)
const strokeDashoffset = computed(() => {
  return circumference.value - (scrollProgress.value / 100) * circumference.value
})

// 处理滚动事件
const handleScroll = () => {
  const scrollTop = window.pageYOffset || document.documentElement.scrollTop
  const documentHeight = document.documentElement.scrollHeight - window.innerHeight
  
  // 更新可见性
  isVisible.value = scrollTop > props.threshold
  
  // 更新滚动进度
  if (props.showProgress && documentHeight > 0) {
    scrollProgress.value = Math.min(100, (scrollTop / documentHeight) * 100)
  }
}

// 滚动到顶部
const scrollToTop = () => {
  if (props.behavior === 'smooth') {
    // 使用自定义平滑滚动
    const startTime = performance.now()
    const startScrollTop = window.pageYOffset
    
    const animateScroll = (currentTime: number) => {
      const elapsed = currentTime - startTime
      const progress = Math.min(elapsed / props.duration, 1)
      
      // 使用缓动函数
      const easeOutCubic = 1 - Math.pow(1 - progress, 3)
      const scrollTop = startScrollTop * (1 - easeOutCubic)
      
      window.scrollTo(0, scrollTop)
      
      if (progress < 1) {
        requestAnimationFrame(animateScroll)
      }
    }
    
    requestAnimationFrame(animateScroll)
  } else {
    window.scrollTo({ top: 0, behavior: props.behavior })
  }
}

// 鼠标事件处理
const handleMouseEnter = () => {
  isHovered.value = true
}

const handleMouseLeave = () => {
  isHovered.value = false
}

// 节流滚动事件
const throttledHandleScroll = throttle(handleScroll, 16) // ~60fps

// 生命周期
onMounted(() => {
  window.addEventListener('scroll', throttledHandleScroll, { passive: true })
  // 初始检查
  handleScroll()
})

onUnmounted(() => {
  window.removeEventListener('scroll', throttledHandleScroll)
})

// 键盘快捷键支持
onMounted(() => {
  const handleKeydown = (event: KeyboardEvent) => {
    // Ctrl/Cmd + Home 键回到顶部
    if ((event.ctrlKey || event.metaKey) && event.key === 'Home') {
      event.preventDefault()
      scrollToTop()
    }
  }
  
  document.addEventListener('keydown', handleKeydown)
  
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })
})

// 工具函数：节流
function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null
  let lastExecTime = 0
  
  return (...args: Parameters<T>) => {
    const currentTime = Date.now()
    
    if (currentTime - lastExecTime > delay) {
      func(...args)
      lastExecTime = currentTime
    } else {
      if (timeoutId) clearTimeout(timeoutId)
      timeoutId = setTimeout(() => {
        func(...args)
        lastExecTime = Date.now()
      }, delay - (currentTime - lastExecTime))
    }
  }
}
</script>

<style scoped>
.back-to-top-btn {
  @apply fixed bottom-6 right-6 z-40;
  @apply w-12 h-12 bg-blue-500 hover:bg-blue-600 text-white;
  @apply rounded-full shadow-lg hover:shadow-xl;
  @apply flex items-center justify-center;
  @apply transition-all duration-300 ease-out;
  @apply transform hover:scale-110 active:scale-95;
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
}

.back-to-top-btn--extended {
  @apply w-14 h-14;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .back-to-top-btn {
    @apply bottom-4 right-4 w-10 h-10;
  }
  
  .back-to-top-btn--extended {
    @apply w-12 h-12;
  }
}

/* 深色模式优化 */
@media (prefers-color-scheme: dark) {
  .back-to-top-btn {
    @apply bg-blue-600 hover:bg-blue-700;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .back-to-top-btn {
    @apply transition-none;
  }
  
  .back-to-top-btn:hover {
    @apply transform-none;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .back-to-top-btn {
    @apply border-2 border-white;
  }
}
</style>