<template>
  <div class="platform-selector" :class="selectorClass">
    <!-- 标签 -->
    <label v-if="label" class="platform-selector__label">
      {{ label }}
    </label>

    <!-- 单选模式 -->
    <template v-if="!multiple">
      <!-- 下拉选择器 -->
      <USelectMenu
        v-if="variant === 'dropdown'"
        v-model="selectedValue"
        :options="platformOptions"
        :placeholder="placeholder"
        :disabled="disabled"
        :loading="loading"
        :searchable="searchable"
        :clearable="clearable"
        option-attribute="display_name"
        value-attribute="code"
        class="platform-selector__dropdown"
      >
        <template #label>
          <div v-if="selectedPlatform" class="flex items-center space-x-2">
            <Icon 
              v-if="selectedPlatform.icon" 
              :name="selectedPlatform.icon" 
              class="w-4 h-4"
            />
            <span>{{ selectedPlatform.display_name }}</span>
          </div>
          <span v-else>{{ placeholder }}</span>
        </template>
        
        <template #option="{ option }">
          <div class="flex items-center space-x-2">
            <Icon 
              v-if="option.icon" 
              :name="option.icon" 
              class="w-4 h-4"
            />
            <span>{{ option.display_name }}</span>
            <span v-if="showCount && option.count" class="text-xs text-gray-500">
              ({{ formatCount(option.count) }})
            </span>
          </div>
        </template>
      </USelectMenu>

      <!-- 标签页模式 -->
      <UTabs
        v-else-if="variant === 'tabs'"
        v-model="selectedTabIndex"
        :items="tabItems"
        class="platform-selector__tabs"
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
          </div>
        </template>
      </UTabs>

      <!-- 按钮组模式 -->
      <div v-else-if="variant === 'buttons'" class="platform-selector__buttons">
        <UButton
          v-for="platform in visiblePlatforms"
          :key="platform.code"
          :label="platform.display_name"
          :icon="platform.icon"
          :variant="selectedValue === platform.code ? 'solid' : 'outline'"
          :color="selectedValue === platform.code ? 'primary' : 'gray'"
          :size="size"
          :disabled="disabled"
          @click="selectPlatform(platform.code)"
        >
          <template v-if="showCount && platform.count" #trailing>
            <UBadge 
              :label="formatCount(platform.count)"
              size="xs"
              :color="selectedValue === platform.code ? 'white' : 'gray'"
              :variant="selectedValue === platform.code ? 'solid' : 'soft'"
            />
          </template>
        </UButton>
        
        <!-- 更多按钮 -->
        <UDropdown v-if="hasMorePlatforms" :items="moreDropdownItems">
          <UButton
            icon="heroicons:ellipsis-horizontal"
            variant="outline"
            color="gray"
            :size="size"
            :disabled="disabled"
          />
        </UDropdown>
      </div>

      <!-- 卡片模式 -->
      <div v-else-if="variant === 'cards'" class="platform-selector__cards">
        <div
          v-for="platform in platformOptions"
          :key="platform.code"
          class="platform-card"
          :class="{
            'platform-card--selected': selectedValue === platform.code,
            'platform-card--disabled': disabled
          }"
          @click="!disabled && selectPlatform(platform.code)"
        >
          <div class="platform-card__icon">
            <Icon 
              v-if="platform.icon" 
              :name="platform.icon" 
              class="w-8 h-8"
            />
          </div>
          <div class="platform-card__content">
            <h3 class="platform-card__title">{{ platform.display_name }}</h3>
            <p v-if="platform.description" class="platform-card__description">
              {{ platform.description }}
            </p>
            <div v-if="showCount && platform.count" class="platform-card__count">
              {{ formatCount(platform.count) }} 条内容
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- 多选模式 -->
    <template v-else>
      <!-- 复选框组 -->
      <div class="platform-selector__checkboxes">
        <UCheckbox
          v-for="platform in platformOptions"
          :key="platform.code"
          v-model="selectedValues"
          :value="platform.code"
          :label="platform.display_name"
          :disabled="disabled"
        >
          <template #label>
            <div class="flex items-center space-x-2">
              <Icon 
                v-if="platform.icon" 
                :name="platform.icon" 
                class="w-4 h-4"
              />
              <span>{{ platform.display_name }}</span>
              <span v-if="showCount && platform.count" class="text-xs text-gray-500">
                ({{ formatCount(platform.count) }})
              </span>
            </div>
          </template>
        </UCheckbox>
      </div>
    </template>

    <!-- 快速筛选 -->
    <div v-if="showQuickFilters" class="platform-selector__quick-filters">
      <UButton
        label="全部"
        variant="ghost"
        size="xs"
        :color="!selectedValue ? 'primary' : 'gray'"
        @click="clearSelection"
      />
      <UButton
        v-for="filter in quickFilters"
        :key="filter.code"
        :label="filter.label"
        :icon="filter.icon"
        variant="ghost"
        size="xs"
        :color="selectedValue === filter.code ? 'primary' : 'gray'"
        @click="selectPlatform(filter.code)"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Platform } from '~/types'

interface Props {
  modelValue?: string | string[]
  platforms?: readonly Platform[]
  variant?: 'dropdown' | 'tabs' | 'buttons' | 'cards'
  size?: 'xs' | 'sm' | 'md' | 'lg'
  multiple?: boolean
  label?: string
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  searchable?: boolean
  clearable?: boolean
  showCount?: boolean
  showQuickFilters?: boolean
  maxVisible?: number
  quickFilters?: Array<{ code: string; label: string; icon?: string }>
  class?: string
}

interface Emits {
  'update:modelValue': [value: string | string[]]
  'change': [value: string | string[], platform: Platform | Platform[]]
}

const props = withDefaults(defineProps<Props>(), {
  variant: 'dropdown',
  size: 'md',
  multiple: false,
  placeholder: '选择平台',
  searchable: true,
  clearable: true,
  showCount: true,
  showQuickFilters: false,
  maxVisible: 5,
  quickFilters: () => [
    { code: 'hot', label: '热门', icon: 'heroicons:fire' },
    { code: 'new', label: '最新', icon: 'heroicons:sparkles' },
    { code: 'trending', label: '趋势', icon: 'heroicons:arrow-trending-up' }
  ]
})

const emit = defineEmits<Emits>()

// 使用组合式函数
const { platforms: defaultPlatforms } = usePlatforms()

// 响应式数据
const selectedTabIndex = ref(0)

// 计算属性
const platformOptions = computed(() => {
  const platforms = props.platforms || defaultPlatforms.value
  return [...platforms] as Platform[]
})

const selectorClass = computed(() => {
  return [
    'platform-selector',
    `platform-selector--${props.variant}`,
    `platform-selector--${props.size}`,
    {
      'platform-selector--multiple': props.multiple,
      'platform-selector--disabled': props.disabled,
      'platform-selector--loading': props.loading
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
      const platforms = platformOptions.value.filter((p: any) => 
        Array.isArray(value) && value.includes(p.code)
      )
      emit('change', value, platforms)
    } else {
      const platform = platformOptions.value.find((p: any) => p.code === value)
      emit('change', value, platform || {} as Platform)
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

const selectedPlatform = computed(() => {
  if (props.multiple) return null
  return platformOptions.value.find((p: any) => p.code === selectedValue.value)
})

const visiblePlatforms = computed(() => {
  return platformOptions.value.slice(0, props.maxVisible)
})

const hasMorePlatforms = computed(() => {
  return platformOptions.value.length > props.maxVisible
})

const moreDropdownItems = computed(() => {
  const morePlatforms = platformOptions.value.slice(props.maxVisible)
  return [morePlatforms.map((platform: any) => ({
    label: platform.display_name,
    icon: platform.icon,
    click: () => selectPlatform(platform.code)
  }))]
})

const tabItems = computed(() => {
  const allTab = {
    key: 'all',
    label: '全部',
    icon: 'heroicons:squares-2x2',
    count: platformOptions.value.reduce((sum: number, p: any) => sum + (p.count || 0), 0)
  }
  
  const platformTabs = platformOptions.value.map((platform: any) => ({
    key: platform.code,
    label: platform.display_name,
    icon: platform.icon,
    count: platform.count
  }))
  
  return [allTab, ...platformTabs]
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

// 选择平台
const selectPlatform = (code: string) => {
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
  selectPlatform,
  clearSelection,
  selectedPlatform,
  selectedValue: readonly(selectedValue)
})
</script>

<style scoped>
.platform-selector {
  @apply w-full;
}

.platform-selector__label {
  @apply block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2;
}

/* 按钮组样式 */
.platform-selector__buttons {
  @apply flex flex-wrap gap-2;
}

/* 卡片样式 */
.platform-selector__cards {
  @apply grid gap-4;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
}

.platform-card {
  @apply bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700;
  @apply rounded-lg p-4 cursor-pointer;
  @apply hover:border-primary-300 dark:hover:border-primary-600;
  @apply hover:shadow-md transition-all duration-200;
}

.platform-card--selected {
  @apply border-primary-500 dark:border-primary-400;
  @apply bg-primary-50 dark:bg-primary-900/20;
  @apply ring-2 ring-primary-200 dark:ring-primary-800;
}

.platform-card--disabled {
  @apply opacity-50 cursor-not-allowed;
  @apply hover:border-gray-200 dark:hover:border-gray-700;
  @apply hover:shadow-none;
}

.platform-card__icon {
  @apply mb-3 text-gray-600 dark:text-gray-400;
}

.platform-card--selected .platform-card__icon {
  @apply text-primary-600 dark:text-primary-400;
}

.platform-card__title {
  @apply text-lg font-semibold text-gray-900 dark:text-white mb-1;
}

.platform-card__description {
  @apply text-sm text-gray-600 dark:text-gray-400 mb-2;
}

.platform-card__count {
  @apply text-xs text-gray-500 dark:text-gray-500;
}

/* 复选框组样式 */
.platform-selector__checkboxes {
  @apply space-y-3;
}

/* 快速筛选样式 */
.platform-selector__quick-filters {
  @apply flex flex-wrap gap-2 mt-3 pt-3;
  @apply border-t border-gray-200 dark:border-gray-700;
}

/* 尺寸变体 */
.platform-selector--xs .platform-card {
  @apply p-3;
}

.platform-selector--xs .platform-card__title {
  @apply text-base;
}

.platform-selector--sm .platform-card {
  @apply p-3;
}

.platform-selector--lg .platform-card {
  @apply p-6;
}

.platform-selector--lg .platform-card__title {
  @apply text-xl;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .platform-selector__cards {
    grid-template-columns: 1fr;
  }
  
  .platform-selector__buttons {
    @apply flex-col;
  }
  
  .platform-card {
    @apply p-3;
  }
  
  .platform-card__title {
    @apply text-base;
  }
}

/* 加载状态 */
.platform-selector--loading {
  @apply opacity-75 pointer-events-none;
}

/* 禁用状态 */
.platform-selector--disabled {
  @apply opacity-50 pointer-events-none;
}

/* 动画效果 */
.platform-card {
  transition: all 0.2s ease-out;
}

.platform-card:hover {
  transform: translateY(-1px);
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .platform-card {
    transition: none;
  }
  
  .platform-card:hover {
    transform: none;
  }
}
</style>