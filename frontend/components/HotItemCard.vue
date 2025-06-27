<template>
  <div 
    class="flex items-center py-2 px-3 hover:bg-gray-50 dark:hover:bg-gray-800 cursor-pointer transition-colors"
    @click="handleClick"
  >
    <!-- 排名 -->
    <div class="w-8 text-center">
      <span 
        class="text-sm font-medium"
        :class="{
          'text-red-500': rank <= 3,
          'text-gray-500': rank > 3
        }"
      >
        {{ rank }}
      </span>
    </div>

    <!-- 标题 -->
    <div class="flex-1 min-w-0 mx-3">
      <h3 class="text-sm text-gray-900 dark:text-gray-100 truncate hover:text-blue-600 dark:hover:text-blue-400">
        {{ item.title }}
      </h3>
    </div>

    <!-- 热度 -->
    <div v-if="item.score" class="text-xs text-gray-500 dark:text-gray-400">
      {{ formatScore(item.score) }}
    </div>
  </div>
</template>

<script setup lang="ts">
import type { HotItem } from '~/types'

interface Props {
  item: HotItem
  rank: number
}

interface Emits {
  'click': [item: HotItem]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 方法
const handleClick = () => {
  if (props.item.url) {
    window.open(props.item.url, '_blank')
  }
  emit('click', props.item)
}

const formatScore = (score: number) => {
  if (score >= 10000) {
    return (score / 10000).toFixed(1) + 'w'
  }
  return score.toString()
}
</script>