<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
    <div class="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md dark:bg-gray-800">
      <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-white">登录</h2>
      <UForm :state="state" :schema="schema" @submit="submit" class="space-y-6">
        <UFormGroup label="邮箱" name="email">
          <UInput v-model="state.email" placeholder="you@example.com" icon="i-heroicons-envelope" />
        </UFormGroup>

        <UFormGroup label="密码" name="password">
          <UInput v-model="state.password" type="password" placeholder="请输入密码" icon="i-heroicons-lock-closed" />
        </UFormGroup>

        <UButton type="submit" block label="登录" :loading="loading" />

        <div class="text-sm text-center">
          <NuxtLink to="/register" class="font-medium text-primary-600 hover:text-primary-500">还没有账户？去注册</NuxtLink>
        </div>
      </UForm>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { z } from 'zod'

const { login } = useAuth()
const router = useRouter()
const { addNotification } = useNotification()

const state = ref({
  email: '',
  password: ''
})

const loading = ref(false)

const schema = z.object({
  email: z.string().email('无效的邮箱地址'),
  password: z.string().min(8, '密码至少需要8个字符')
})

async function submit() {
  loading.value = true
  try {
    const result = await login(state.value.email, state.value.password)
    if (result.success) {
      addNotification('success', '登录成功')
      router.push('/')
    } else {
      addNotification('error', result.error || '登录失败')
    }
  } catch (error) {
    addNotification('error', '登录失败')
  } finally {
    loading.value = false
  }
}
</script>