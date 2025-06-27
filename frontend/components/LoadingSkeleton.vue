<template>
  <div class="loading-skeleton" :class="skeletonClass">
    <!-- 热门条目卡片骨架 -->
    <template v-if="type === 'hot-item'">
      <div class="flex items-start space-x-4 p-4">
        <!-- 排名标识骨架 -->
        <div class="skeleton-rank"></div>
        
        <!-- 主要内容骨架 -->
        <div class="flex-1 space-y-3">
          <!-- 标题和平台信息骨架 -->
          <div class="flex items-start justify-between">
            <div class="space-y-2 flex-1">
              <div class="skeleton-line skeleton-line--title"></div>
              <div class="skeleton-line skeleton-line--subtitle"></div>
            </div>
            <div class="skeleton-platform"></div>
          </div>
          
          <!-- 描述骨架 -->
          <div class="space-y-2">
            <div class="skeleton-line skeleton-line--description"></div>
            <div class="skeleton-line skeleton-line--description skeleton-line--short"></div>
          </div>
          
          <!-- 标签骨架 -->
          <div class="flex space-x-2">
            <div class="skeleton-tag" v-for="i in 3" :key="i"></div>
          </div>
          
          <!-- 统计信息骨架 -->
          <div class="flex items-center space-x-4">
            <div class="skeleton-stat" v-for="i in 4" :key="i"></div>
          </div>
        </div>
        
        <!-- 缩略图骨架 -->
        <div class="skeleton-thumbnail"></div>
      </div>
    </template>

    <!-- 列表项骨架 -->
    <template v-else-if="type === 'list-item'">
      <div class="flex items-center space-x-3 p-3">
        <div class="skeleton-avatar"></div>
        <div class="flex-1 space-y-2">
          <div class="skeleton-line skeleton-line--title"></div>
          <div class="skeleton-line skeleton-line--subtitle skeleton-line--short"></div>
        </div>
        <div class="skeleton-icon"></div>
      </div>
    </template>

    <!-- 卡片骨架 -->
    <template v-else-if="type === 'card'">
      <div class="space-y-4 p-4">
        <div class="skeleton-image skeleton-image--card"></div>
        <div class="space-y-2">
          <div class="skeleton-line skeleton-line--title"></div>
          <div class="skeleton-line skeleton-line--description"></div>
          <div class="skeleton-line skeleton-line--description skeleton-line--short"></div>
        </div>
        <div class="flex items-center justify-between">
          <div class="skeleton-tag"></div>
          <div class="skeleton-icon"></div>
        </div>
      </div>
    </template>

    <!-- 头像骨架 -->
    <template v-else-if="type === 'avatar'">
      <div class="skeleton-avatar" :class="`skeleton-avatar--${size}`"></div>
    </template>

    <!-- 文本行骨架 -->
    <template v-else-if="type === 'text'">
      <div class="space-y-2">
        <div 
          v-for="i in lines" 
          :key="i"
          class="skeleton-line"
          :class="{
            'skeleton-line--short': i === lines && lines > 1
          }"
        ></div>
      </div>
    </template>

    <!-- 图片骨架 -->
    <template v-else-if="type === 'image'">
      <div 
        class="skeleton-image"
        :class="`skeleton-image--${size}`"
        :style="customStyle"
      ></div>
    </template>

    <!-- 按钮骨架 -->
    <template v-else-if="type === 'button'">
      <div 
        class="skeleton-button"
        :class="`skeleton-button--${size}`"
      ></div>
    </template>

    <!-- 表格行骨架 -->
    <template v-else-if="type === 'table-row'">
      <div class="flex items-center space-x-4 p-3">
        <div 
          v-for="i in columns" 
          :key="i"
          class="skeleton-line"
          :class="{
            'flex-1': i === 1,
            'w-20': i === columns,
            'w-32': i > 1 && i < columns
          }"
        ></div>
      </div>
    </template>

    <!-- 统计卡片骨架 -->
    <template v-else-if="type === 'stat-card'">
      <div class="space-y-3 p-4">
        <div class="flex items-center justify-between">
          <div class="skeleton-icon"></div>
          <div class="skeleton-tag"></div>
        </div>
        <div class="skeleton-line skeleton-line--title"></div>
        <div class="skeleton-line skeleton-line--subtitle skeleton-line--short"></div>
      </div>
    </template>

    <!-- 自定义骨架 -->
    <template v-else>
      <div class="skeleton-custom">
        <slot></slot>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
interface Props {
  type?: 'hot-item' | 'list-item' | 'card' | 'avatar' | 'text' | 'image' | 'button' | 'table-row' | 'stat-card' | 'custom'
  size?: 'xs' | 'sm' | 'md' | 'lg' | 'xl'
  lines?: number
  columns?: number
  width?: string | number
  height?: string | number
  rounded?: boolean
  animated?: boolean
  class?: string
}

const props = withDefaults(defineProps<Props>(), {
  type: 'text',
  size: 'md',
  lines: 3,
  columns: 4,
  rounded: true,
  animated: true
})

// 计算属性
const skeletonClass = computed(() => {
  return [
    {
      'skeleton--animated': props.animated,
      'skeleton--rounded': props.rounded
    },
    props.class
  ]
})

const customStyle = computed(() => {
  const style: Record<string, string> = {}
  
  if (props.width) {
    style.width = typeof props.width === 'number' ? `${props.width}px` : props.width
  }
  
  if (props.height) {
    style.height = typeof props.height === 'number' ? `${props.height}px` : props.height
  }
  
  return style
})
</script>

<style scoped>
/* 基础骨架样式 */
.loading-skeleton {
  @apply bg-white dark:bg-gray-800;
  @apply border border-gray-200 dark:border-gray-700;
}

.skeleton--rounded {
  @apply rounded-xl;
}

/* 骨架元素基础样式 */
.skeleton-base {
  @apply bg-gray-200 dark:bg-gray-700;
  @apply relative overflow-hidden;
}

.skeleton--animated .skeleton-base::before {
  content: '';
  @apply absolute inset-0;
  @apply bg-gradient-to-r from-transparent via-white/20 to-transparent;
  @apply transform -translate-x-full;
  animation: shimmer 1.5s infinite;
}

/* 排名标识骨架 */
.skeleton-rank {
  @apply skeleton-base w-8 h-8 rounded-full;
  @apply flex-shrink-0;
}

/* 文本行骨架 */
.skeleton-line {
  @apply skeleton-base h-4 rounded;
}

.skeleton-line--title {
  @apply h-5 w-3/4;
}

.skeleton-line--subtitle {
  @apply h-4 w-1/2;
}

.skeleton-line--description {
  @apply h-3 w-full;
}

.skeleton-line--short {
  @apply w-2/3;
}

/* 平台信息骨架 */
.skeleton-platform {
  @apply skeleton-base w-20 h-6 rounded-full;
}

/* 标签骨架 */
.skeleton-tag {
  @apply skeleton-base w-12 h-6 rounded-full;
}

/* 统计信息骨架 */
.skeleton-stat {
  @apply skeleton-base w-16 h-4 rounded;
}

/* 缩略图骨架 */
.skeleton-thumbnail {
  @apply skeleton-base w-20 h-20 rounded-lg;
  @apply flex-shrink-0;
}

/* 头像骨架 */
.skeleton-avatar {
  @apply skeleton-base rounded-full;
  @apply flex-shrink-0;
}

.skeleton-avatar--xs {
  @apply w-6 h-6;
}

.skeleton-avatar--sm {
  @apply w-8 h-8;
}

.skeleton-avatar--md {
  @apply w-10 h-10;
}

.skeleton-avatar--lg {
  @apply w-12 h-12;
}

.skeleton-avatar--xl {
  @apply w-16 h-16;
}

/* 图片骨架 */
.skeleton-image {
  @apply skeleton-base rounded-lg;
}

.skeleton-image--xs {
  @apply w-16 h-16;
}

.skeleton-image--sm {
  @apply w-20 h-20;
}

.skeleton-image--md {
  @apply w-32 h-32;
}

.skeleton-image--lg {
  @apply w-48 h-48;
}

.skeleton-image--xl {
  @apply w-64 h-64;
}

.skeleton-image--card {
  @apply w-full h-48;
}

/* 按钮骨架 */
.skeleton-button {
  @apply skeleton-base rounded-lg;
}

.skeleton-button--xs {
  @apply w-16 h-6;
}

.skeleton-button--sm {
  @apply w-20 h-8;
}

.skeleton-button--md {
  @apply w-24 h-10;
}

.skeleton-button--lg {
  @apply w-32 h-12;
}

.skeleton-button--xl {
  @apply w-40 h-14;
}

/* 图标骨架 */
.skeleton-icon {
  @apply skeleton-base w-5 h-5 rounded;
}

/* 自定义骨架 */
.skeleton-custom {
  @apply space-y-2;
}

/* 动画 */
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .skeleton--animated .skeleton-base::before {
    animation: none;
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .skeleton-thumbnail {
    @apply w-16 h-16;
  }
  
  .skeleton-line--title {
    @apply w-full;
  }
  
  .skeleton-line--subtitle {
    @apply w-3/4;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .skeleton-base {
    @apply bg-gray-400 dark:bg-gray-600;
  }
}
</style>