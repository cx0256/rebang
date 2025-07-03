import type { Notification, NotificationAction } from '~/types'

export const useNotification = () => {
  // 通知列表状态
  const notifications = useState<Notification[]>('notifications', () => [])
  
  // 生成唯一ID
  const generateId = () => {
    return Math.random().toString(36).substring(2, 15) + Math.random().toString(36).substring(2, 15)
  }
  
  // 添加通知
  const addNotification = (
    type: Notification['type'],
    title: string,
    message?: string,
    duration?: number,
    actions?: NotificationAction[]
  ) => {
    const notification: Notification = {
      id: generateId(),
      type,
      title,
      message,
      duration: duration ?? (type === 'error' ? 0 : 5000), // 错误通知不自动消失
      actions,
      createdAt: Date.now()
    }
    
    notifications.value.push(notification)
    
    // 自动移除通知
    if (notification.duration && notification.duration > 0) {
      setTimeout(() => {
        removeNotification(notification.id)
      }, notification.duration)
    }
    
    return notification.id
  }
  
  // 移除通知
  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }
  
  // 清除所有通知
  const clearNotifications = () => {
    notifications.value = []
  }
  
  // 清除指定类型的通知
  const clearNotificationsByType = (type: Notification['type']) => {
    notifications.value = notifications.value.filter(n => n.type !== type)
  }
  
  // 成功通知
  const success = (title: string, message?: string, duration?: number) => {
    return addNotification('success', title, message, duration)
  }
  
  // 错误通知
  const error = (title: string, message?: string, duration?: number) => {
    return addNotification('error', title, message, duration)
  }
  
  // 警告通知
  const warning = (title: string, message?: string, duration?: number) => {
    return addNotification('warning', title, message, duration)
  }
  
  // 信息通知
  const info = (title: string, message?: string, duration?: number) => {
    return addNotification('info', title, message, duration)
  }
  
  // 确认对话框
  const confirm = (
    title: string,
    message?: string,
    confirmText = '确认',
    cancelText = '取消'
  ): Promise<boolean> => {
    return new Promise((resolve) => {
      const actions: NotificationAction[] = [
        {
          label: cancelText,
          action: () => {
            resolve(false)
          },
          style: 'secondary'
        },
        {
          label: confirmText,
          action: () => {
            resolve(true)
          },
          style: 'primary'
        }
      ]
      
      addNotification('warning', title, message, 0, actions)
    })
  }
  
  // 提示对话框
  const alert = (title: string, message?: string, buttonText = '确定'): Promise<void> => {
    return new Promise((resolve) => {
      const actions: NotificationAction[] = [
        {
          label: buttonText,
          action: () => {
            resolve()
          },
          style: 'primary'
        }
      ]
      
      addNotification('info', title, message, 0, actions)
    })
  }
  
  // 加载通知
  const loading = (title: string, message?: string) => {
    const id = addNotification('info', title, message, 0)
    
    return {
      id,
      close: () => removeNotification(id),
      update: (newTitle: string, newMessage?: string) => {
        const notification = notifications.value.find(n => n.id === id)
        if (notification) {
          notification.title = newTitle
          notification.message = newMessage
        }
      }
    }
  }
  
  // 进度通知
  const progress = (title: string, initialProgress = 0) => {
    const id = addNotification('info', title, `进度: ${initialProgress}%`, 0)
    
    return {
      id,
      close: () => removeNotification(id),
      update: (progress: number, message?: string) => {
        const notification = notifications.value.find(n => n.id === id)
        if (notification) {
          notification.message = message || `进度: ${progress}%`
        }
      },
      complete: (message = '完成') => {
        const notification = notifications.value.find(n => n.id === id)
        if (notification) {
          notification.type = 'success'
          notification.message = message
          notification.duration = 3000
          
          setTimeout(() => {
            removeNotification(id)
          }, 3000)
        }
      },
      fail: (message = '失败') => {
        const notification = notifications.value.find(n => n.id === id)
        if (notification) {
          notification.type = 'error'
          notification.message = message
        }
      }
    }
  }
  
  // 网络状态通知
  const networkStatus = () => {
    let offlineNotificationId: string | null = null
    
    const handleOnline = () => {
      if (offlineNotificationId) {
        removeNotification(offlineNotificationId)
        offlineNotificationId = null
      }
      success('网络已连接', '您现在可以正常使用所有功能', 3000)
    }
    
    const handleOffline = () => {
      offlineNotificationId = error(
        '网络连接断开',
        '请检查您的网络连接，部分功能可能无法使用',
        0
      )
    }
    
    // 监听网络状态
    if (process.client) {
      window.addEventListener('online', handleOnline)
      window.addEventListener('offline', handleOffline)
      
      // 初始检查
      if (!navigator.onLine) {
        handleOffline()
      }
    }
    
    return {
      cleanup: () => {
        if (process.client) {
          window.removeEventListener('online', handleOnline)
          window.removeEventListener('offline', handleOffline)
        }
        if (offlineNotificationId) {
          removeNotification(offlineNotificationId)
        }
      }
    }
  }
  
  // API错误处理
  const handleApiError = (error: any, defaultMessage = '操作失败') => {
    let title = defaultMessage
    let message = ''
    
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 400:
          title = '请求错误'
          message = data.message || '请求参数有误'
          break
        case 401:
          title = '未授权'
          message = '请先登录'
          break
        case 403:
          title = '访问被拒绝'
          message = '您没有权限执行此操作'
          break
        case 404:
          title = '资源不存在'
          message = '请求的资源未找到'
          break
        case 422:
          title = '验证失败'
          message = data.detail || '输入数据有误'
          break
        case 429:
          title = '请求过于频繁'
          message = '请稍后再试'
          break
        case 500:
          title = '服务器错误'
          message = '服务器内部错误，请稍后重试'
          break
        default:
          title = `错误 ${status}`
          message = data.message || '未知错误'
      }
    } else if (error.request) {
      title = '网络错误'
      message = '无法连接到服务器，请检查网络连接'
    } else {
      title = defaultMessage
      message = error.message || '未知错误'
    }
    
    return error(title, message)
  }
  
  // 批量操作结果通知
  const batchResult = (results: { success: number; failed: number; total: number }) => {
    const { success: successCount, failed: failedCount, total } = results
    
    if (failedCount === 0) {
      success('操作完成', `成功处理 ${successCount} 项`)
    } else if (successCount === 0) {
      error('操作失败', `${failedCount} 项操作失败`)
    } else {
      warning(
        '操作部分完成',
        `成功 ${successCount} 项，失败 ${failedCount} 项，共 ${total} 项`
      )
    }
  }
  
  return {
    // 状态
    notifications: readonly(notifications),
    
    // 基础方法
    addNotification,
    removeNotification,
    clearNotifications,
    clearNotificationsByType,
    
    // 快捷方法
    success,
    error,
    warning,
    info,
    confirm,
    alert,
    loading,
    progress,
    
    // 高级功能
    networkStatus,
    handleApiError,
    batchResult
  }
}