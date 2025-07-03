<template>
  <div class="category-tree-node" :class="nodeClass">
    <!-- 节点内容 -->
    <div 
      class="category-tree-node__content"
      :class="{
        'category-tree-node__content--selected': isSelected,
        'category-tree-node__content--disabled': disabled
      }"
      @click="handleClick"
    >
      <!-- 展开/收起按钮 -->
      <button
        v-if="hasChildren"
        class="category-tree-node__toggle"
        :class="{ 'category-tree-node__toggle--expanded': isExpanded }"
        @click.stop="toggleExpanded"
      >
        <Icon 
          name="heroicons:chevron-right" 
          class="w-4 h-4 transition-transform duration-200"
          :class="{ 'rotate-90': isExpanded }"
        />
      </button>
      
      <!-- 占位符（无子节点时） -->
      <div v-else class="category-tree-node__spacer"></div>

      <!-- 分类图标 -->
      <div class="category-tree-node__icon">
        <Icon 
          v-if="category.icon" 
          :name="category.icon" 
          class="w-4 h-4"
        />
      </div>

      <!-- 分类名称 -->
      <span class="category-tree-node__name">
        {{ category.display_name }}
      </span>

      <!-- 数量标识 -->
      <span 
        v-if="showCount && category.count" 
        class="category-tree-node__count"
      >
        ({{ formatCount(category.count) }})
      </span>

      <!-- 热门标识 -->
      <UBadge 
        v-if="category.is_hot" 
        label="热" 
        size="xs" 
        :color="'red' as any" 
        variant="soft"
        class="category-tree-node__hot-badge"
      />

      <!-- 新增标识 -->
      <UBadge 
        v-if="category.is_new" 
        label="新" 
        size="xs" 
        :color="'blue' as any" 
        variant="soft"
        class="category-tree-node__new-badge"
      />
    </div>

    <!-- 子节点 -->
    <Transition
      name="category-tree-expand"
      @enter="onEnter"
      @after-enter="onAfterEnter"
      @leave="onLeave"
      @after-leave="onAfterLeave"
    >
      <div 
        v-if="hasChildren && isExpanded" 
        class="category-tree-node__children"
      >
        <CategoryTreeNode
          v-for="child in children"
          :key="child.code"
          :category="child"
          :selected="selected"
          :show-count="showCount"
          :disabled="disabled"
          :level="level + 1"
          :max-level="maxLevel"
          @select="$emit('select', $event)"
        />
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import type { Category } from '~/types'

interface Props {
  category: Category
  selected?: string
  showCount?: boolean
  disabled?: boolean
  level?: number
  maxLevel?: number
  defaultExpanded?: boolean
}

interface Emits {
  'select': [code: string]
}

const props = withDefaults(defineProps<Props>(), {
  showCount: true,
  disabled: false,
  level: 0,
  maxLevel: 3,
  defaultExpanded: false
})

const emit = defineEmits<Emits>()

// 使用组合式函数
const categories = ref<Category[]>([])

// 响应式数据
const isExpanded = ref(props.defaultExpanded || props.level === 0)

// 计算属性
const nodeClass = computed(() => {
  return [
    'category-tree-node',
    `category-tree-node--level-${props.level}`,
    {
      'category-tree-node--expanded': isExpanded.value,
      'category-tree-node--selected': isSelected.value,
      'category-tree-node--disabled': props.disabled,
      'category-tree-node--has-children': hasChildren.value
    }
  ]
})

const isSelected = computed(() => {
  return props.selected === props.category.code
})

const children = computed(() => {
  return categories.value.filter((cat: Category) => cat.parent_code === props.category.code)
})

const hasChildren = computed(() => {
  return children.value.length > 0 && props.level < props.maxLevel
})

// 格式化数量
const formatCount = (count: number) => {
  if (count >= 10000) {
    return `${(count / 10000).toFixed(1)}万`
  }
  if (count >= 1000) {
    return `${(count / 1000).toFixed(1)}k`
  }
  return count.toString()
}

// 事件处理
const handleClick = () => {
  if (props.disabled) return
  emit('select', props.category.code)
}

const toggleExpanded = () => {
  if (!hasChildren.value) return
  isExpanded.value = !isExpanded.value
}

// 动画钩子
const onEnter = (el: Element) => {
  const element = el as HTMLElement
  element.style.height = '0'
  element.style.overflow = 'hidden'
}

const onAfterEnter = (el: Element) => {
  const element = el as HTMLElement
  element.style.height = 'auto'
  element.style.overflow = 'visible'
}

const onLeave = (el: Element) => {
  const element = el as HTMLElement
  element.style.height = `${element.scrollHeight}px`
  element.style.overflow = 'hidden'
  // 强制重排
  element.offsetHeight
  element.style.height = '0'
}

const onAfterLeave = (el: Element) => {
  const element = el as HTMLElement
  element.style.height = 'auto'
  element.style.overflow = 'visible'
}

// 监听选中状态变化，自动展开父节点
watch(() => props.selected, (newSelected) => {
  if (newSelected && children.value.some((child: Category) => 
    child.code === newSelected || 
    isDescendantSelected(child, newSelected)
  )) {
    isExpanded.value = true
  }
}, { immediate: true })

// 检查是否有后代被选中
const isDescendantSelected = (category: Category, selectedCode: string): boolean => {
  const descendants = categories.value.filter((cat: Category) => cat.parent_code === category.code)
  return descendants.some((desc: any) => 
    desc.code === selectedCode || isDescendantSelected(desc, selectedCode)
  )
}

// 暴露方法
defineExpose({
  expand: () => { isExpanded.value = true },
  collapse: () => { isExpanded.value = false },
  toggle: toggleExpanded,
  isExpanded: readonly(isExpanded)
})
</script>

<style scoped>
.category-tree-node {
  @apply select-none;
}

.category-tree-node__content {
  @apply flex items-center space-x-2 py-2 px-3;
  @apply rounded-md cursor-pointer;
  @apply hover:bg-gray-100 dark:hover:bg-gray-800;
  @apply transition-colors duration-200;
}

.category-tree-node__content--selected {
  @apply bg-primary-100 dark:bg-primary-900/30;
  @apply text-primary-700 dark:text-primary-300;
  @apply font-medium;
}

.category-tree-node__content--disabled {
  @apply opacity-50 cursor-not-allowed;
  @apply hover:bg-transparent;
}

.category-tree-node__toggle {
  @apply p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700;
  @apply transition-colors duration-200;
  @apply flex-shrink-0;
}

.category-tree-node__spacer {
  @apply w-6 flex-shrink-0;
}

.category-tree-node__icon {
  @apply flex-shrink-0 text-gray-500 dark:text-gray-400;
}

.category-tree-node__content--selected .category-tree-node__icon {
  @apply text-primary-600 dark:text-primary-400;
}

.category-tree-node__name {
  @apply flex-1 text-sm text-gray-700 dark:text-gray-300;
  @apply truncate;
}

.category-tree-node__content--selected .category-tree-node__name {
  @apply text-primary-700 dark:text-primary-300;
}

.category-tree-node__count {
  @apply text-xs text-gray-500 dark:text-gray-400;
  @apply flex-shrink-0;
}

.category-tree-node__hot-badge,
.category-tree-node__new-badge {
  @apply flex-shrink-0;
}

.category-tree-node__children {
  @apply ml-4 border-l border-gray-200 dark:border-gray-700;
  @apply pl-2;
}

/* 层级样式 */
.category-tree-node--level-0 .category-tree-node__content {
  @apply font-medium;
}

.category-tree-node--level-1 .category-tree-node__content {
  @apply text-sm;
}

.category-tree-node--level-2 .category-tree-node__content {
  @apply text-xs;
}

.category-tree-node--level-3 .category-tree-node__content {
  @apply text-xs opacity-90;
}

/* 展开/收起动画 */
.category-tree-expand-enter-active,
.category-tree-expand-leave-active {
  transition: height 0.3s ease-out;
}

.category-tree-expand-enter-from,
.category-tree-expand-leave-to {
  height: 0;
  overflow: hidden;
}

/* 悬浮效果 */
.category-tree-node__content:hover .category-tree-node__icon {
  @apply text-gray-600 dark:text-gray-300;
}

.category-tree-node__content--selected:hover .category-tree-node__icon {
  @apply text-primary-600 dark:text-primary-400;
}

/* 焦点样式 */
.category-tree-node__content:focus-visible {
  @apply outline-none ring-2 ring-primary-500 ring-offset-2;
  @apply ring-offset-white dark:ring-offset-gray-900;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .category-tree-node__content {
    @apply py-3 px-2;
  }
  
  .category-tree-node__name {
    @apply text-xs;
  }
  
  .category-tree-node__count {
    @apply text-xs;
  }
  
  .category-tree-node__children {
    @apply ml-2 pl-1;
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .category-tree-expand-enter-active,
  .category-tree-expand-leave-active {
    transition: none;
  }
  
  .category-tree-node__toggle {
    transition: none;
  }
  
  .category-tree-node__content {
    transition: none;
  }
}

/* 高对比度模式 */
@media (prefers-contrast: high) {
  .category-tree-node__content {
    @apply border border-transparent;
  }
  
  .category-tree-node__content--selected {
    @apply border-primary-600;
  }
  
  .category-tree-node__content:hover {
    @apply border-gray-400;
  }
}
</style>