export default defineNuxtRouteMiddleware((to, from) => {
  // 获取认证状态
  const { isAuthenticated, user } = useAuth()
  
  // 定义需要认证的路由
  const protectedRoutes = [
    '/admin',
    '/profile',
    '/settings',
    '/dashboard'
  ]
  
  // 定义管理员专用路由
  const adminRoutes = [
    '/admin'
  ]
  
  // 检查是否为受保护的路由
  const isProtectedRoute = protectedRoutes.some(route => 
    to.path.startsWith(route)
  )
  
  // 检查是否为管理员路由
  const isAdminRoute = adminRoutes.some(route => 
    to.path.startsWith(route)
  )
  
  // 如果是受保护的路由但用户未认证
  if (isProtectedRoute && !isAuthenticated.value) {
    // 保存原始路径用于登录后重定向
    const redirectPath = useCookie('redirect-path', {
      default: () => '/'
    })
    redirectPath.value = to.fullPath
    
    // 重定向到登录页
    return navigateTo('/login')
  }
  
  // 如果是管理员路由但用户不是管理员
  if (isAdminRoute && (!isAuthenticated.value || !user.value?.is_admin)) {
    // 显示错误提示
    throw createError({
      statusCode: 403,
      statusMessage: '访问被拒绝：需要管理员权限'
    })
  }
  
  // 如果已登录用户访问登录页，重定向到首页
  if (to.path === '/login' && isAuthenticated.value) {
    return navigateTo('/')
  }
})