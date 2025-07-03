<template>
  <div class="flex items-center justify-center min-h-screen bg-gray-100 dark:bg-gray-900">
    <div class="w-full max-w-md p-8 space-y-6 bg-white rounded-lg shadow-md dark:bg-gray-800">
      <h2 class="text-2xl font-bold text-center text-gray-900 dark:text-white">注册</h2>
      <UForm :state="state" :schema="schema" @submit="submit" class="space-y-6">
        <UFormGroup label="用户名" name="username">
          <UInput v-model="state.username" placeholder="请输入用户名" icon="i-heroicons-user" />
        </UFormGroup>

        <UFormGroup label="邮箱" name="email">
          <UInput v-model="state.email" placeholder="you@example.com" icon="i-heroicons-envelope" />
        </UFormGroup>

        <UFormGroup label="密码" name="password">
          <UInput v-model="state.password" type="password" placeholder="请输入密码" icon="i-heroicons-lock-closed" />
        </UFormGroup>

        <UFormGroup label="确认密码" name="passwordConfirm">
          <UInput v-model="state.passwordConfirm" type="password" placeholder="请再次输入密码" icon="i-heroicons-lock-closed" />
        </UFormGroup>

        <UButton type="submit" block label="注册" :loading="loading" />

        <div class="text-sm text-center">
          <NuxtLink to="/login" class="font-medium text-primary-600 hover:text-primary-500">已有账户？去登录</NuxtLink>
        </div>
      </UForm>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { z } from 'zod'

const { register } = useAuth()
const router = useRouter()
const notification = useNotification()

const state = ref({
  username: '',
  email: '',
  password: '',
  passwordConfirm: ''
})

const loading = ref(false)

const schema = z.object({
  username: z.string().min(3, '用户名至少需要3个字符'),
  email: z.string().email('无效的邮箱地址'),
  password: z.string().min(8, '密码至少需要8个字符'),
  passwordConfirm: z.string().min(8, '密码至少需要8个字符')
}).refine((data) => data.password === data.passwordConfirm, {
  message: "两次输入的密码不一致",
  path: ["passwordConfirm"],
});

async function submit() {
  loading.value = true
  try {
    await register(state.value)
    notification.success({ title: '注册成功', message: '欢迎加入！请登录。' })
    router.push('/login')
  } catch (error) {
    notification.error({ title: '注册失败', message: error.data?.detail || '发生了未知错误' })
  } finally {
    loading.value = false
  }
}
</script>