<template>
  <div class="category-selector" :class="selectorClass">
    <!-- 标签 -->
    <label v-if="label" class="category-selector__label">
      {{ label }}
    </label>

    <!-- 单选模式 -->
    <template v-if="!multiple">
      <!-- 下拉选择器 -->
      <USelectMenu
        v-if="variant === 'dropdown'"
        v-model="selectedValue"
        :options="categoryOptions"
        :placeholder="placeholder"
        :disabled="disabled"
        :loading="loading"
        :searchable="searchable"
        :clearable="clearable"
        option-attribute="display_name"
        value-attribute="code"
        class="category-selector__dropdown"
      >
        <template #label>
          <div v-if="selectedCategory" class="flex items-center space-x-2">
            <Icon 
              v-if="selectedCategory.icon" 
              :name="selectedCategory.icon" 
              class="w-4 h-4"
            />
            <span>{{ selectedCategory.display_name }}</span>
          </div>
          <span v-else>{{ placeholder }}</span>
        </template>
        
        <template #option="{ option }">
          <div class="flex items-center justify-between w-full">
            <div class="flex items-center space-x-2">
              <Icon 
                v-if="option.icon" 
                :name="option.icon" 
                class="w-4 h-4"
              />
              <span>{{ option.display_name }}</span>
            </div>
            <div class="flex items-center space-x-2">
              <span v-if="showCount && option.count" class="text-xs text-gray-500">
                {{ formatCount(option.count) }}
              </span>
              <UBadge 
                v-if="option.is_hot" 
                label="热门" 
                size="xs" 
                :color="'red' as any" 
                variant="soft"
              />
            </div>
          </div>
        </template>
      </USelectMenu>

      <!-- 标签页模式 -->
      <UTabs
        v-else-if="variant === 'tabs'"
        v-model="selectedTabIndex"
        :items="tabItems"
        class="category-selector__tabs"
      >
        <template #item="{ item }">
          <div class="flex items-center space-x-2">
            <Icon 
              v-if="item.icon" 
              :name="item.icon" 
              class="w-4 h-4"
            />
            <span>{{ item.label }}</span>
            <UBadge 
              v-if="showCount && item.count" 
              :label="formatCount(item.count)"
              size="xs"
              color="gray"
              variant="soft"
            />
            <UBadge 
              v-if="item.is_hot" 
              label="热门" 
              size="xs" 
              :color="'red' as any" 
              variant="soft"
            />
          </div>
        </template>
      </UTabs>

      <!-- 按钮组模式 -->
      <div v-else-if="variant === 'buttons'" class="category-selector__buttons">
        <UButton
          v-for="category in visibleCategories"
          :key="category.code"
          :variant="selectedValue === category.code ? 'solid' : 'outline'"
          :color="selectedValue === category.code ? 'primary' : 'gray'"
          :size="size"
          :disabled="disabled"
          @click="selectCategory(category.code)"
        >
          <template #leading>
            <Icon 
              v-if="category.icon" 
              :name="category.icon" 
              class="w-4 h-4"
            />
          </template>
          
          {{ category.display_name }}
          
          <template #trailing>
            <div class="flex items-center space-x-1">
              <UBadge 
                v-if="showCount && category.count"
                :label="formatCount(category.count)"
                size="xs"
                :color="selectedValue === category.code ? 'white' : 'gray'"
                :variant="selectedValue === category.code ? 'solid' : 'soft'"
              />
              <UBadge 
                v-if="category.is_hot" 
                label="热" 
                size="xs" 
                :color="'red' as any" 
                variant="solid"
              />
            </div>
          </template>
        </UButton>
        
        <!-- 更多按钮 -->
        <UDropdown v-if="hasMoreCategories" :items="moreDropdownItems">
          <UButton
            icon="heroicons:ellipsis-horizontal"
            variant="outline"
            color="gray"
            :size="size"
            :disabled="disabled"
          />
        </UDropdown>
      </div>

      <!-- 网格模式 -->
      <div v-else-if="variant === 'grid'" class="category-selector__grid">
        <div
          v-for="category in categoryOptions"
          :key="category.code"
          class="category-card"
          :class="{
            'category-card--selected': selectedValue === category.code,
            'category-card--disabled': disabled,
            'category-card--hot': category.is_hot
          }"
          @click="!disabled && selectCategory(category.code)"
        >
          <div class="category-card__icon">
            <Icon 
              v-if="category.icon" 
              :name="category.icon" 
              class="w-6 h-6"
            />
          </div>
          <div class="category-card__content">
            <h3 class="category-card__title">{{ category.display_name }}</h3>
            <p v-if="category.description" class="category-card__description">
              {{ category.description }}
            </p>
            <div class="category-card__meta">
              <span v-if="showCount && category.count" class="category-card__count">
                {{ formatCount(category.count) }} 条
              </span>
              <UBadge 
                v-if="category.is_hot" 
                label="热门" 
                size="xs" 
                :color="'red' as any" 
                variant="soft"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 树形模式 -->
      <div v-else-if="variant === 'tree'" class="category-selector__tree">
        <CategoryTreeNode
          v-for="category in rootCategories"
          :key="category.code"
          :category="category"
          :selected="Array.isArray(selectedValue) ? selectedValue[0] : selectedValue"
          :show-count="showCount"
          :disabled="disabled"
          @select="selectCategory"
        />
      </div>
    </template>

    <!-- 多选模式 -->
    <template v-else>
      <!-- 复选框组 -->
      <div class="category-selector__checkboxes">
        <UCheckbox
          v-for="category in categoryOptions"
          :key="category.code"
          v-model="selectedValues"
          :value="category.code"
          :disabled="disabled"
        >
          <template #label>
            <div class="flex items-center justify-between w-full">
              <div class="flex items-center space-x-2">
                <Icon 
                  v-if="category.icon" 
                  :name="category.icon" 
                  class="w-4 h-4"
                />
                <span>{{ category.display_name }}</span>
              </div>
              <div class="flex items-center space-x-2">
                <span v-if="showCount && category.count" class="text-xs text-gray-500">
                  {{ formatCount(category.count) }}
                </span>
                <UBadge 
                  v-if="category.is_hot" 
                  label="热" 
                  size="xs" 
                  :color="'red' as any" 
                  variant="soft"
                />
              </div>
            </div>
          </template>
        </UCheckbox>
      </div>
    </template>

    <!-- 热门分类快捷选择 -->
    <div v-if="showHotCategories && hotCategories.length > 0" class="category-selector__hot">
      <h4 class="category-selector__hot-title">
        <Icon name="heroicons:fire" class="w-4 h-4 text-red-500" />
        热门分类
      </h4>
      <div class="category-selector__hot-list">
        <UButton
          v-for="category in hotCategories"
          :key="category.code"
          :label="category.display_name"
          :icon="category.icon"
          variant="ghost"
          size="xs"
          :color="selectedValue === category.code ? 'primary' : 'gray'"
          @click="selectCategory(category.code)"
        />
      </div>
    </div>

    <!-- 搜索框 -->
    <div v-if="showSearch" class="category-selector__search">
      <UInput
        v-model="searchQuery"
        placeholder="搜索分类..."
        icon="heroicons:magnifying-glass"
        :disabled="disabled"
        size="sm"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Category } from '~/types'

interface Props {
  modelValue?: string | string[]
  categories?: readonly Category[]
  variant?: 'dropdown' | 'tabs' | 'buttons' | 'grid' | 'tree'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  multiple?: boolean
  label?: string
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  searchable?: boolean
  clearable?: boolean
  showCount?: boolean
  showHotCategories?: boolean
  showSearch?: boolean
  maxVisible?: number
  class?: string
}

interface Emits {
  'update:modelValue': [value: string | string[]]
  'change': [value: string | string[], category: Category | Category[] | null]
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'dropdown',
  size: 'md',
  multiple: false,
  placeholder: '选择分类',
  searchable: true,
  clearable: true,
  showCount: true,
  showHotCategories: true,
  showSearch: false,
  maxVisible: 6
})

const emit = defineEmits<Emits>()

// 使用组合式函数
const defaultCategories = ref<Category[]>([])

// 响应式数据
const selectedTabIndex = ref(0)
const searchQuery = ref('')

// 计算属性
const categoryOptions = computed(() => {
  let categories = [...(props.categories || defaultCategories.value)]
  
  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    categories = categories.filter((category: any) => 
      category.display_name.toLowerCase().includes(query) ||
      category.description?.toLowerCase().includes(query)
    )
  }
  
  return categories
})

const selectorClass = computed(() => {
  return [
    'category-selector',
    `category-selector--${props.variant}`,
    `category-selector--${props.size}`,
    {
      'category-selector--multiple': props.multiple,
      'category-selector--disabled': props.disabled,
      'category-selector--loading': props.loading
    },
    props.class
  ]
})

const selectedValue = computed({
  get: () => {
    if (props.multiple) {
      return Array.isArray(props.modelValue) ? props.modelValue : []
    }
    return props.modelValue as string
  },
  set: (value) => {
    emit('update:modelValue', value)
    
    // 发出 change 事件
    if (props.multiple) {
      const categories = categoryOptions.value.filter((c: any) => 
        Array.isArray(value) && value.includes(c.code)
      )
      emit('change', value, categories)
    } else {
      const category = categoryOptions.value.find((c: any) => c.code === value)
      emit('change', value, category || null as Category | null)
    }
  }
})

const selectedValues = computed({
  get: () => {
    return Array.isArray(props.modelValue) ? props.modelValue : []
  },
  set: (value) => {
    selectedValue.value = value
  }
})

const selectedCategory = computed(() => {
  if (props.multiple) return null
  return categoryOptions.value.find((c: any) => c.code === selectedValue.value)
})

const visibleCategories = computed(() => {
  return categoryOptions.value.slice(0, props.maxVisible)
})

const hasMoreCategories = computed(() => {
  return categoryOptions.value.length > props.maxVisible
})

const moreDropdownItems = computed(() => {
  const moreCategories = categoryOptions.value.slice(props.maxVisible)
  return [moreCategories.map((category: any) => ({
    label: category.display_name,
    icon: category.icon,
    click: () => selectCategory(category.code)
  }))]
})

const tabItems = computed(() => {
  const allTab = {
    key: 'all',
    label: '全部',
    icon: 'heroicons:squares-2x2',
    count: categoryOptions.value.reduce((sum: number, c: any) => sum + (c.count || 0), 0),
    is_hot: false
  }
  
  const categoryTabs = categoryOptions.value.map((category: any) => ({
    key: category.code,
    label: category.display_name,
    icon: category.icon,
    count: category.count,
    is_hot: category.is_hot
  }))
  
  return [allTab, ...categoryTabs]
})

const hotCategories = computed(() => {
  return categoryOptions.value.filter((category: any) => category.is_hot)
})

const rootCategories = computed(() => {
  return categoryOptions.value.filter((category: any) => !category.parent_code)
})

// 监听标签页变化
watch(selectedTabIndex, (newIndex) => {
  const selectedTab = tabItems.value[newIndex]
  if (selectedTab) {
    const value = selectedTab.key === 'all' ? '' : selectedTab.key
    selectedValue.value = value
  }
})

// 监听选中值变化（用于同步标签页）
watch(() => props.modelValue, (newValue) => {
  if (props.variant === 'tabs') {
    const index = tabItems.value.findIndex(tab => 
      tab.key === (newValue || 'all')
    )
    if (index !== -1) {
      selectedTabIndex.value = index
    }
  }
}, { immediate: true })

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

// 选择分类
const selectCategory = (code: string) => {
  if (props.disabled) return
  
  if (props.multiple) {
    const currentValues = Array.isArray(selectedValue.value) ? selectedValue.value : []
    const newValues = currentValues.includes(code)
      ? currentValues.filter(v => v !== code)
      : [...currentValues, code]
    selectedValue.value = newValues
  } else {
    selectedValue.value = selectedValue.value === code ? '' : code
  }
}

// 清除选择
const clearSelection = () => {
  selectedValue.value = props.multiple ? [] : ''
}

// 暴露方法
defineExpose({
  selectCategory,
  clearSelection,
  selectedCategory,
  selectedValue: readonly(selectedValue)
})
</script>

<style scoped>
.category-selector {
  @apply w-full;
}

.category-selector__label {
  @apply block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2;
}

/* 按钮组样式 */
.category-selector__buttons {
  @apply flex flex-wrap gap-2;
}

/* 网格样式 */
.category-selector__grid {
  @apply grid gap-3;
  grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
}

.category-card {
  @apply bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700;
  @apply rounded-lg p-3 cursor-pointer;
  @apply hover:border-primary-300 dark:hover:border-primary-600;
  @apply hover:shadow-md transition-all duration-200;
  @apply relative;
}

.category-card--selected {
  @apply border-primary-500 dark:border-primary-400;
  @apply bg-primary-50 dark:bg-primary-900/20;
  @apply ring-2 ring-primary-200 dark:ring-primary-800;
}

.category-card--disabled {
  @apply opacity-50 cursor-not-allowed;
  @apply hover:border-gray-200 dark:hover:border-gray-700;
  @apply hover:shadow-none;
}

.category-card--hot::before {
  content: '';
  @apply absolute -top-1 -right-1 w-2 h-2;
  @apply bg-red-500 rounded-full;
}

.category-card__icon {
  @apply mb-2 text-gray-600 dark:text-gray-400;
}

.category-card--selected .category-card__icon {
  @apply text-primary-600 dark:text-primary-400;
}

.category-card__title {
  @apply text-sm font-medium text-gray-900 dark:text-white mb-1;
}

.category-card__description {
  @apply text-xs text-gray-600 dark:text-gray-400 mb-2 line-clamp-2;
}

.category-card__meta {
  @apply flex items-center justify-between;
}

.category-card__count {
  @apply text-xs text-gray-500 dark:text-gray-500;
}

/* 复选框组样式 */
.category-selector__checkboxes {
  @apply space-y-3;
}

/* 热门分类样式 */
.category-selector__hot {
  @apply mt-4 pt-4 border-t border-gray-200 dark:border-gray-700;
}

.category-selector__hot-title {
  @apply flex items-center space-x-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2;
}

.category-selector__hot-list {
  @apply flex flex-wrap gap-2;
}

/* 搜索框样式 */
.category-selector__search {
  @apply mb-4;
}

/* 树形样式 */
.category-selector__tree {
  @apply space-y-1;
}

/* 尺寸变体 */
.category-selector--xs .category-card {
  @apply p-2;
}

.category-selector--xs .category-card__title {
  @apply text-xs;
}

.category-selector--sm .category-card {
  @apply p-2;
}

.category-selector--lg .category-card {
  @apply p-4;
}

.category-selector--lg .category-card__title {
  @apply text-base;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .category-selector__grid {
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    @apply gap-2;
  }
  
  .category-selector__buttons {
    @apply flex-col;
  }
  
  .category-card {
    @apply p-2;
  }
  
  .category-card__title {
    @apply text-xs;
  }
}

/* 加载状态 */
.category-selector--loading {
  @apply opacity-75 pointer-events-none;
}

/* 禁用状态 */
.category-selector--disabled {
  @apply opacity-50 pointer-events-none;
}

/* 动画效果 */
.category-card {
  transition: all 0.2s ease-out;
}

.category-card:hover {
  transform: translateY(-1px);
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .category-card {
    transition: none;
  }
  
  .category-card:hover {
    transform: none;
  }
}
</style>