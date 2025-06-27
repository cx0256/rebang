<template>
  <div class="relative">
    <!-- 搜索输入框 -->
    <div class="relative">
      <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <Icon
          name="heroicons:magnifying-glass"
          class="w-5 h-5 text-gray-400"
        />
      </div>
      <input
        ref="inputRef"
        v-model="localValue"
        type="text"
        class="search-input"
        :class="{
          'pr-20': showClearButton || loading,
          'pr-10': !showClearButton && !loading
        }"
        :placeholder="placeholder"
        :disabled="disabled"
        @input="handleInput"
        @keydown="handleKeydown"
        @focus="handleFocus"
        @blur="handleBlur"
      >
      
      <!-- 右侧按钮区域 -->
      <div class="absolute inset-y-0 right-0 flex items-center">
        <!-- 加载指示器 -->
        <div v-if="loading" class="pr-3">
          <Icon
            name="heroicons:arrow-path"
            class="w-4 h-4 text-gray-400 animate-spin"
          />
        </div>
        
        <!-- 清除按钮 -->
        <button
          v-else-if="showClearButton"
          class="pr-3 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
          @click="clearInput"
        >
          <Icon name="heroicons:x-mark" class="w-4 h-4" />
        </button>
        
        <!-- 搜索按钮 -->
        <button
          v-if="showSearchButton"
          class="pr-3 text-gray-400 hover:text-blue-500 transition-colors"
          :disabled="!localValue.trim() || loading"
          @click="handleSearch"
        >
          <Icon name="heroicons:arrow-right" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- 搜索建议下拉框 -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-2"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-2"
    >
      <div
        v-if="showSuggestions && suggestions.length > 0"
        class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto"
      >
        <div class="py-1">
          <button
            v-for="(suggestion, index) in suggestions"
            :key="index"
            class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center space-x-2"
            :class="{
              'bg-gray-100 dark:bg-gray-700': index === selectedSuggestionIndex
            }"
            @click="selectSuggestion(suggestion)"
            @mouseenter="selectedSuggestionIndex = index"
          >
            <Icon name="heroicons:magnifying-glass" class="w-4 h-4 text-gray-400" />
            <span>{{ suggestion }}</span>
          </button>
        </div>
      </div>
    </Transition>

    <!-- 搜索历史 -->
    <Transition
      enter-active-class="transition-all duration-200 ease-out"
      enter-from-class="opacity-0 scale-95 -translate-y-2"
      enter-to-class="opacity-100 scale-100 translate-y-0"
      leave-active-class="transition-all duration-150 ease-in"
      leave-from-class="opacity-100 scale-100 translate-y-0"
      leave-to-class="opacity-0 scale-95 -translate-y-2"
    >
      <div
        v-if="showHistory && searchHistory.length > 0 && !localValue.trim()"
        class="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg z-50 max-h-60 overflow-y-auto"
      >
        <div class="py-1">
          <div class="px-4 py-2 text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">
            搜索历史
          </div>
          <button
            v-for="(item, index) in searchHistory"
            :key="index"
            class="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-center justify-between group"
            @click="selectHistory(item)"
          >
            <div class="flex items-center space-x-2">
              <Icon name="heroicons:clock" class="w-4 h-4 text-gray-400" />
              <span>{{ item }}</span>
            </div>
            <span
              class="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all cursor-pointer"
              @click.stop="removeFromHistory(item)"
            >
              <Icon name="heroicons:x-mark" class="w-3 h-3" />
            </span>
          </button>
          <div class="border-t border-gray-200 dark:border-gray-700 mt-1 pt-1">
            <button
              class="w-full px-4 py-2 text-left text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 transition-colors"
              @click="clearHistory"
            >
              清除搜索历史
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
interface Props {
  modelValue?: string
  placeholder?: string
  disabled?: boolean
  loading?: boolean
  autofocus?: boolean
  showSearchButton?: boolean
  showSuggestions?: boolean
  showHistory?: boolean
  suggestions?: string[]
  debounceMs?: number
}

interface Emits {
  'update:modelValue': [value: string]
  'search': [query: string]
  'input': [value: string]
  'focus': [event: FocusEvent]
  'blur': [event: FocusEvent]
  'clear': []
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '搜索...',
  disabled: false,
  loading: false,
  autofocus: false,
  showSearchButton: true,
  showSuggestions: true,
  showHistory: true,
  suggestions: () => [],
  debounceMs: 300
})

const emit = defineEmits<Emits>()

// 响应式数据
const inputRef = ref<HTMLInputElement>()
const localValue = ref(props.modelValue)
const isFocused = ref(false)
const selectedSuggestionIndex = ref(-1)
const searchHistory = ref<string[]>([])

// 计算属性
const showClearButton = computed(() => {
  return localValue.value.length > 0 && !props.loading
})

const showSuggestions = computed(() => {
  return props.showSuggestions && isFocused.value && localValue.value.trim().length > 0
})

const showHistory = computed(() => {
  return props.showHistory && isFocused.value && localValue.value.trim().length === 0
})

// 防抖搜索
const debouncedSearch = useDebounceFn((query: string) => {
  emit('search', query)
}, props.debounceMs)

// 事件处理
const handleInput = (event: Event) => {
  const target = event.target as HTMLInputElement
  localValue.value = target.value
  emit('update:modelValue', target.value)
  emit('input', target.value)
  
  // 重置建议选择索引
  selectedSuggestionIndex.value = -1
  
  // 防抖搜索
  if (target.value.trim()) {
    debouncedSearch(target.value.trim())
  }
}

const handleKeydown = (event: KeyboardEvent) => {
  switch (event.key) {
    case 'Enter':
      event.preventDefault()
      if (selectedSuggestionIndex.value >= 0 && props.suggestions.length > 0) {
        selectSuggestion(props.suggestions[selectedSuggestionIndex.value])
      } else {
        handleSearch()
      }
      break
      
    case 'ArrowDown':
      event.preventDefault()
      if (props.suggestions.length > 0) {
        selectedSuggestionIndex.value = Math.min(
          selectedSuggestionIndex.value + 1,
          props.suggestions.length - 1
        )
      }
      break
      
    case 'ArrowUp':
      event.preventDefault()
      if (props.suggestions.length > 0) {
        selectedSuggestionIndex.value = Math.max(
          selectedSuggestionIndex.value - 1,
          -1
        )
      }
      break
      
    case 'Escape':
      inputRef.value?.blur()
      break
  }
}

const handleFocus = (event: FocusEvent) => {
  isFocused.value = true
  emit('focus', event)
}

const handleBlur = (event: FocusEvent) => {
  // 延迟隐藏建议，以便点击建议项
  setTimeout(() => {
    isFocused.value = false
    selectedSuggestionIndex.value = -1
  }, 200)
  emit('blur', event)
}

const handleSearch = () => {
  const query = localValue.value.trim()
  if (query && !props.loading) {
    addToHistory(query)
    emit('search', query)
  }
}

const clearInput = () => {
  localValue.value = ''
  emit('update:modelValue', '')
  emit('clear')
  inputRef.value?.focus()
}

const selectSuggestion = (suggestion: string) => {
  localValue.value = suggestion
  emit('update:modelValue', suggestion)
  addToHistory(suggestion)
  emit('search', suggestion)
  inputRef.value?.blur()
}

const selectHistory = (item: string) => {
  localValue.value = item
  emit('update:modelValue', item)
  emit('search', item)
  inputRef.value?.blur()
}

// 搜索历史管理
const addToHistory = (query: string) => {
  if (!query.trim()) return
  
  // 移除重复项
  const filtered = searchHistory.value.filter(item => item !== query)
  // 添加到开头
  searchHistory.value = [query, ...filtered].slice(0, 10) // 最多保存10条
  
  // 保存到本地存储
  if (process.client) {
    localStorage.setItem('search-history', JSON.stringify(searchHistory.value))
  }
}

const removeFromHistory = (item: string) => {
  searchHistory.value = searchHistory.value.filter(h => h !== item)
  
  // 更新本地存储
  if (process.client) {
    localStorage.setItem('search-history', JSON.stringify(searchHistory.value))
  }
}

const clearHistory = () => {
  searchHistory.value = []
  
  // 清除本地存储
  if (process.client) {
    localStorage.removeItem('search-history')
  }
}

// 加载搜索历史
const loadHistory = () => {
  if (process.client) {
    try {
      const saved = localStorage.getItem('search-history')
      if (saved) {
        searchHistory.value = JSON.parse(saved)
      }
    } catch (error) {
      console.error('Failed to load search history:', error)
    }
  }
}

// 监听 modelValue 变化
watch(
  () => props.modelValue,
  (newValue) => {
    localValue.value = newValue
  }
)

// 自动聚焦
watch(
  () => props.autofocus,
  (autofocus) => {
    if (autofocus) {
      nextTick(() => {
        inputRef.value?.focus()
      })
    }
  },
  { immediate: true }
)

// 生命周期
onMounted(() => {
  loadHistory()
  
  if (props.autofocus) {
    nextTick(() => {
      inputRef.value?.focus()
    })
  }
})

// 暴露方法
defineExpose({
  focus: () => inputRef.value?.focus(),
  blur: () => inputRef.value?.blur(),
  clear: clearInput
})
</script>

<style scoped>
.search-input {
  @apply w-full pl-10 pr-10 py-2 border border-gray-300 dark:border-gray-600;
  @apply bg-white dark:bg-gray-700 text-gray-900 dark:text-white;
  @apply placeholder-gray-500 dark:placeholder-gray-400;
  @apply rounded-lg shadow-sm;
  @apply focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent;
  @apply disabled:bg-gray-100 dark:disabled:bg-gray-800 disabled:cursor-not-allowed;
  @apply transition-all duration-200;
}

.search-input:hover:not(:disabled) {
  @apply border-gray-400 dark:border-gray-500;
}
</style>