import type { User, UserCreate } from '~/types'

export const useAuth = () => {
  const { $api } = useNuxtApp()
  
  const user = useState<User | null>('auth.user', () => null)
  const token = useCookie<string | null>('auth-token', {
    default: () => null,
    maxAge: 60 * 60 * 24 * 7, // 7天
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict'
  })
  
  const isAuthenticated = computed(() => !!user.value && !!token.value)
  const isAdmin = computed(() => user.value?.is_admin || false)
  
  async function login(email: string, password: string) {
    try {
      const formData = new FormData()
      formData.append('username', email) // The form field is 'username' for OAuth2
      formData.append('password', password)

      const response = await $api.post<{ access_token: string; token_type: string }>('/v1/auth/login', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      }) as unknown as { access_token: string; token_type: string; detail?: string }

      if (response.access_token) {
        token.value = response.access_token
        await fetchUser()
        return { success: true }
      } else {
        return { success: false, error: response.detail || '登录失败' }
      }
    } catch (error: any) {
      return { success: false, error: error.message || '登录时发生错误' }
    }
  }
  
  async function register(userData: UserCreate) {
    try {
      const response = await $api.post<{ message: string }>('/v1/auth/register', userData)
      
      if (response) {
        return { success: true, message: response.message || 'Registration successful' }
      } else {
        return { success: false, error: 'Registration failed' }
      }
    } catch (error: any) {
      return { 
        success: false, 
        error: error.response?.data?.detail || error.message || 'Registration failed' 
      }
    }
  }

  async function fetchUser() {
    if (token.value) {
      try {
        const response = await $api.get<User>('/v1/auth/me')
        if (response) {
          user.value = response as unknown as User
        } else {
          token.value = null
          user.value = null
        }
      } catch (error) {
        token.value = null
        user.value = null
      }
    }
  }
  
  // 登出
  const logout = async () => {
    try {
      // 调用后端登出接口
      if (token.value) {
        await $api.post('/v1/auth/logout')
      }
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      // 清除本地状态
      token.value = null
      user.value = null
      
      // 清除重定向路径
      const redirectPath = useCookie('redirect-path')
      redirectPath.value = null
      
      // 重定向到首页
      await navigateTo('/')
    }
  }
  
  // 刷新用户信息
  const refreshUser = async () => {
    try {
      if (!token.value) return false
      
      const response = await $api.get('/v1/auth/me')
      
      if (response.success && response.data) {
        user.value = response.data
        return true
      } else {
        // token可能已过期
        await logout()
        return false
      }
    } catch (error) {
      console.error('Refresh user error:', error)
      await logout()
      return false
    }
  }
  
  // 更新最后登录时间
  const updateLastLogin = async () => {
    try {
      await $api.patch('/v1/auth/last-login')
    } catch (error) {
      console.error('Update last login error:', error)
    }
  }
  
  // 修改密码
  const changePassword = async (oldPassword: string, newPassword: string) => {
    try {
      const response = await $api.patch('/v1/auth/change-password', {
        old_password: oldPassword,
        new_password: newPassword
      })
      
      if (response.success) {
        return { success: true, message: '密码修改成功' }
      } else {
        throw new Error(response.message || '密码修改失败')
      }
    } catch (error: any) {
      console.error('Change password error:', error)
      return {
        success: false,
        error: error.message || '密码修改失败'
      }
    }
  }
  
  // 更新用户资料
  const updateProfile = async (profileData: Partial<User>) => {
    try {
      const response = await $api.patch('/v1/auth/profile', profileData)
      
      if (response.success && response.data) {
        user.value = response.data
        return { success: true, message: '资料更新成功' }
      } else {
        throw new Error(response.message || '资料更新失败')
      }
    } catch (error: any) {
      console.error('Update profile error:', error)
      return {
        success: false,
        error: error.message || '资料更新失败'
      }
    }
  }
  
  // 忘记密码
  const forgotPassword = async (email: string) => {
    try {
      const response = await $api.post('/v1/auth/forgot-password', { email })
      
      if (response.success) {
        return { success: true, message: '重置密码邮件已发送' }
      } else {
        throw new Error(response.message || '发送失败')
      }
    } catch (error: any) {
      console.error('Forgot password error:', error)
      return {
        success: false,
        error: error.message || '发送失败，请稍后重试'
      }
    }
  }
  
  // 重置密码
  const resetPassword = async (token: string, newPassword: string) => {
    try {
      const response = await $api.post('/v1/auth/reset-password', {
        token,
        new_password: newPassword
      })
      
      if (response.success) {
        return { success: true, message: '密码重置成功，请登录' }
      } else {
        throw new Error(response.message || '密码重置失败')
      }
    } catch (error: any) {
      console.error('Reset password error:', error)
      return {
        success: false,
        error: error.message || '密码重置失败'
      }
    }
  }
  
  // 验证token有效性
  const validateToken = async () => {
    try {
      if (!token.value) return false
      
      const response = await $api.get('/v1/auth/validate')
      return response.success
    } catch (error) {
      console.error('Validate token error:', error)
      return false
    }
  }
  
  // 初始化认证状态
  const initAuth = async () => {
    if (token.value && !user.value) {
      const isValid = await validateToken()
      if (isValid) {
        await refreshUser()
      } else {
        await logout()
      }
    }
  }
  
  // 检查权限
  const hasPermission = (permission: string) => {
    if (!user.value) return false
    if (user.value.is_admin) return true
    
    // 这里可以根据实际需求扩展权限检查逻辑
    return false
  }
  
  // 检查角色
  const hasRole = (role: string) => {
    if (!user.value) return false
    
    switch (role) {
      case 'admin':
        return user.value.is_admin
      case 'user':
        return user.value.is_active
      default:
        return false
    }
  }
  
  return {
    // 状态
    user: readonly(user),
    token: readonly(token),
    isAuthenticated,
    isAdmin,
    
    // 方法
    login,
    register,
    logout,
    refreshUser,
    changePassword,
    updateProfile,
    forgotPassword,
    resetPassword,
    validateToken,
    initAuth,
    hasPermission,
    hasRole
  }
}