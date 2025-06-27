<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 主要内容区域 -->
    <main class="w-full">
      <slot />
    </main>
    
    <!-- 底部 -->
    <!-- <AppFooter /> -->
    
    <!-- 通知组件 -->
    <NotificationContainer />
    
    <!-- 回到顶部按钮 -->
    <BackToTop />
  </div>
</template>

<script setup lang="ts">
// 页面元数据
useHead({
  htmlAttrs: {
    lang: 'zh-CN'
  },
  bodyAttrs: {
    class: 'antialiased'
  }
})

// 初始化认证状态
const { initAuth } = useAuth()
onMounted(() => {
  initAuth()
})

// 网络状态监听
const { networkStatus } = useNotification()
const networkMonitor = networkStatus()

// 清理资源
onUnmounted(() => {
  networkMonitor.cleanup()
})
</script>

<style scoped>
/* 布局特定样式 */
</style>