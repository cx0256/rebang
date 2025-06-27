<template>
  <div class="empty-state" :class="emptyStateClass">
    <!-- 图标或插图 -->
    <div class="empty-state__icon">
      <slot name="icon">
        <Icon 
          :name="iconName" 
          :class="iconClass"
        />
      </slot>
    </div>

    <!-- 标题 -->
    <h3 class="empty-state__title">
      <slot name="title">
        {{ title }}
      </slot>
    </h3>

    <!-- 描述 -->
    <p v-if="description || $slots.description" class="empty-state__description">
      <slot name="description">
        {{ description }}
      </slot>
    </p>

    <!-- 操作按钮 -->
    <div v-if="showActions" class="empty-state__actions">
      <slot name="actions">
        <!-- 主要操作 -->
        <UButton
          v-if="primaryAction"
          :label="primaryAction.label"
          :icon="primaryAction.icon"
          :loading="primaryAction.loading"
          :disabled="primaryAction.disabled"
          color="primary"
          size="lg"
          @click="handlePrimaryAction"
        />
        
        <!-- 次要操作 -->
        <UButton
          v-if="secondaryAction"
          :label="secondaryAction.label"
          :icon="secondaryAction.icon"
          :loading="secondaryAction.loading"
          :disabled="secondaryAction.disabled"
          color="gray"
          variant="ghost"
          size="lg"
          @click="handleSecondaryAction"
        />
      </slot>
    </div>

    <!-- 额外内容 -->
    <div v-if="$slots.extra" class="empty-state__extra">
      <slot name="extra"></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
interface ActionConfig {
  label: string
  icon?: string
  loading?: boolean
  disabled?: boolean
  handler?: () => void | Promise<void>
}

interface Props {
  type?: 'no-data' | 'no-results' | 'error' | 'network-error' | 'permission' | 'maintenance' | 'custom'
  title?: string
  description?: string
  icon?: string
  size?: 'sm' | 'md' | 'lg'
  showActions?: boolean
  primaryAction?: ActionConfig
  secondaryAction?: ActionConfig
  class?: string
}

interface Emits {
  'primary-action': []
  'secondary-action': []
}

const props = withDefaults(defineProps<Props>(), {
  type: 'no-data',
  size: 'md',
  showActions: true
})

const emit = defineEmits<Emits>()

// 计算属性
const emptyStateClass = computed(() => {
  return [
    'empty-state',
    `empty-state--${props.size}`,
    `empty-state--${props.type}`,
    props.class
  ]
})

const iconName = computed(() => {
  if (props.icon) return props.icon
  
  switch (props.type) {
    case 'no-data':
      return 'heroicons:document-text'
    case 'no-results':
      return 'heroicons:magnifying-glass'
    case 'error':
      return 'heroicons:exclamation-triangle'
    case 'network-error':
      return 'heroicons:wifi'
    case 'permission':
      return 'heroicons:lock-closed'
    case 'maintenance':
      return 'heroicons:wrench-screwdriver'
    default:
      return 'heroicons:document-text'
  }
})

const iconClass = computed(() => {
  const baseClass = 'empty-state__icon-svg'
  const sizeClass = {
    sm: 'w-12 h-12',
    md: 'w-16 h-16',
    lg: 'w-20 h-20'
  }[props.size]
  
  const typeClass = {
    'no-data': 'text-gray-400',
    'no-results': 'text-blue-400',
    'error': 'text-red-400',
    'network-error': 'text-orange-400',
    'permission': 'text-yellow-400',
    'maintenance': 'text-purple-400',
    'custom': 'text-gray-400'
  }[props.type]
  
  return [baseClass, sizeClass, typeClass]
})

const title = computed(() => {
  if (props.title) return props.title
  
  switch (props.type) {
    case 'no-data':
      return '暂无数据'
    case 'no-results':
      return '没有找到相关内容'
    case 'error':
      return '出现错误'
    case 'network-error':
      return '网络连接失败'
    case 'permission':
      return '权限不足'
    case 'maintenance':
      return '系统维护中'
    default:
      return '暂无内容'
  }
})

const description = computed(() => {
  if (props.description) return props.description
  
  switch (props.type) {
    case 'no-data':
      return '当前没有可显示的数据，请稍后再试或添加新内容'
    case 'no-results':
      return '尝试调整搜索条件或浏览其他内容'
    case 'error':
      return '系统遇到了一些问题，请稍后重试'
    case 'network-error':
      return '请检查网络连接并重试'
    case 'permission':
      return '您没有访问此内容的权限，请联系管理员'
    case 'maintenance':
      return '系统正在维护中，预计很快恢复正常'
    default:
      return ''
  }
})

// 事件处理
const handlePrimaryAction = async () => {
  if (props.primaryAction?.handler) {
    await props.primaryAction.handler()
  }
  emit('primary-action')
}

const handleSecondaryAction = async () => {
  if (props.secondaryAction?.handler) {
    await props.secondaryAction.handler()
  }
  emit('secondary-action')
}
</script>

<style scoped>
.empty-state {
  @apply flex flex-col items-center justify-center;
  @apply text-center;
  @apply py-12 px-6;
}

/* 尺寸变体 */
.empty-state--sm {
  @apply py-8 px-4;
}

.empty-state--md {
  @apply py-12 px-6;
}

.empty-state--lg {
  @apply py-16 px-8;
}

/* 图标容器 */
.empty-state__icon {
  @apply mb-4;
}

.empty-state__icon-svg {
  @apply mx-auto;
}

/* 标题 */
.empty-state__title {
  @apply text-lg font-semibold text-gray-900 dark:text-white;
  @apply mb-2;
}

.empty-state--sm .empty-state__title {
  @apply text-base;
}

.empty-state--lg .empty-state__title {
  @apply text-xl;
}

/* 描述 */
.empty-state__description {
  @apply text-sm text-gray-600 dark:text-gray-400;
  @apply max-w-md mx-auto;
  @apply leading-relaxed;
  @apply mb-6;
}

.empty-state--sm .empty-state__description {
  @apply text-xs mb-4;
}

.empty-state--lg .empty-state__description {
  @apply text-base mb-8;
}

/* 操作按钮 */
.empty-state__actions {
  @apply flex flex-col sm:flex-row items-center justify-center;
  @apply space-y-2 sm:space-y-0 sm:space-x-3;
  @apply mb-4;
}

.empty-state--sm .empty-state__actions {
  @apply mb-2;
}

.empty-state--lg .empty-state__actions {
  @apply mb-6;
}

/* 额外内容 */
.empty-state__extra {
  @apply text-sm text-gray-500 dark:text-gray-400;
}

/* 类型特定样式 */
.empty-state--error {
  @apply bg-red-50 dark:bg-red-900/10;
  @apply border border-red-200 dark:border-red-800;
  @apply rounded-lg;
}

.empty-state--network-error {
  @apply bg-orange-50 dark:bg-orange-900/10;
  @apply border border-orange-200 dark:border-orange-800;
  @apply rounded-lg;
}

.empty-state--permission {
  @apply bg-yellow-50 dark:bg-yellow-900/10;
  @apply border border-yellow-200 dark:border-yellow-800;
  @apply rounded-lg;
}

.empty-state--maintenance {
  @apply bg-purple-50 dark:bg-purple-900/10;
  @apply border border-purple-200 dark:border-purple-800;
  @apply rounded-lg;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .empty-state {
    @apply py-8 px-4;
  }
  
  .empty-state__title {
    @apply text-base;
  }
  
  .empty-state__description {
    @apply text-xs;
  }
  
  .empty-state__actions {
    @apply flex-col space-y-2 space-x-0;
  }
}

/* 动画效果 */
.empty-state {
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
  .empty-state {
    animation: none;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .empty-state__title {
    @apply text-black dark:text-white;
  }
  
  .empty-state__description {
    @apply text-gray-800 dark:text-gray-200;
  }
}
</style>