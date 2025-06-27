<template>
  <button
    class="theme-toggle"
    :title="`切换到${isDark ? '浅色' : '深色'}模式`"
    @click="toggleTheme"
  >
    <!-- 太阳图标 (浅色模式) -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 scale-0 rotate-90"
      enter-to-class="opacity-100 scale-100 rotate-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100 rotate-0"
      leave-to-class="opacity-0 scale-0 -rotate-90"
    >
      <Icon
        v-if="!isDark"
        name="heroicons:sun"
        class="w-5 h-5 text-yellow-500"
      />
    </Transition>

    <!-- 月亮图标 (深色模式) -->
    <Transition
      enter-active-class="transition-all duration-300 ease-out"
      enter-from-class="opacity-0 scale-0 -rotate-90"
      enter-to-class="opacity-100 scale-100 rotate-0"
      leave-active-class="transition-all duration-200 ease-in"
      leave-from-class="opacity-100 scale-100 rotate-0"
      leave-to-class="opacity-0 scale-0 rotate-90"
    >
      <Icon
        v-if="isDark"
        name="heroicons:moon"
        class="w-5 h-5 text-blue-400"
      />
    </Transition>
  </button>
</template>

<script setup lang="ts">
// 使用 Nuxt 的颜色模式
const colorMode = useColorMode()

// 计算属性 - 添加安全检查
const isDark = computed(() => colorMode?.value === 'dark')

// 切换主题
const toggleTheme = () => {
  if (colorMode) {
    colorMode.preference = isDark.value ? 'light' : 'dark'
  }
}

// 键盘快捷键支持
onMounted(() => {
  const handleKeydown = (event: KeyboardEvent) => {
    // Ctrl/Cmd + Shift + T 切换主题
    if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'T') {
      event.preventDefault()
      toggleTheme()
    }
  }
  
  document.addEventListener('keydown', handleKeydown)
  
  onUnmounted(() => {
    document.removeEventListener('keydown', handleKeydown)
  })
})
</script>

<style scoped>
.theme-toggle {
  @apply relative p-2 rounded-lg;
  @apply text-gray-600 dark:text-gray-300;
  @apply hover:text-gray-900 dark:hover:text-white;
  @apply hover:bg-gray-100 dark:hover:bg-gray-700;
  @apply transition-all duration-200 ease-out;
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2;
  @apply dark:focus:ring-offset-gray-800;
}

.theme-toggle:active {
  @apply scale-95;
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .theme-toggle {
    @apply transition-none;
  }
  
  .theme-toggle:active {
    @apply transform-none;
  }
}
</style>