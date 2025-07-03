import axios, { type AxiosInstance, type AxiosRequestConfig, type AxiosResponse } from 'axios'
import type { ApiResponse } from '~/types'

class ApiClient {
  private instance: AxiosInstance

  constructor() {
    const runtimeConfig = useRuntimeConfig()
    const baseURL = runtimeConfig.public.apiBase

    this.instance = axios.create({
      baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // 请求拦截器
    this.instance.interceptors.request.use(
      (config) => {
        // 添加认证token
        const token = useCookie('auth-token').value
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // 添加请求ID用于追踪
        config.headers['X-Request-ID'] = generateRequestId()

        // 开发环境下打印请求信息
        if (process.dev) {
          const fullUrl = `${config.baseURL}${config.url}`
          console.log(`🚀 API Request: ${config.method?.toUpperCase()} ${fullUrl}`, {
            params: config.params,
            data: config.data
          })
        }

        return config
      },
      (error) => {
        console.error('❌ Request Error:', error)
        return Promise.reject(error)
      }
    )

    // 响应拦截器
    this.instance.interceptors.response.use(
      (response: AxiosResponse) => {
        // 开发环境下打印响应信息
        if (process.dev) {
          const fullUrl = `${response.config.baseURL}${response.config.url}`
          console.log(`✅ API Response: ${response.config.method?.toUpperCase()} ${fullUrl}`, {
            status: response.status,
            data: response.data
          })
        }

        return response
      },
      (error) => {
        // 统一错误处理
        const { response } = error
        
        if (response) {
          const { status, data } = response
          
          // 根据状态码处理不同错误
          switch (status) {
            case 401:
              // 未授权，清除token并跳转登录
              const authToken = useCookie('auth-token')
              authToken.value = null
              navigateTo('/login')
              break
            case 403:
              // 禁止访问
              console.error('❌ Access Forbidden:', data.message)
              break
            case 404:
              // 资源不存在
              console.error('❌ Resource Not Found:', data.message)
              break
            case 422:
              // 验证错误
              console.error('❌ Validation Error:', data.detail)
              break
            case 429:
              // 请求过于频繁
              console.error('❌ Too Many Requests:', data.message)
              break
            case 500:
              // 服务器错误
              console.error('❌ Server Error:', data.message)
              break
            default:
              console.error(`❌ API Error (${status}):`, data.message || error.message)
          }
        } else if (error.request) {
          // 网络错误
          console.error('❌ Network Error:', error.message)
        } else {
          // 其他错误
          console.error('❌ Unknown Error:', error.message)
        }

        return Promise.reject(error)
      }
    )
  }

  // GET 请求
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.get(url, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // POST 请求
  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.post(url, data, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // PUT 请求
  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.put(url, data, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // PATCH 请求
  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.patch(url, data, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // DELETE 请求
  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    try {
      const response = await this.instance.delete(url, config)
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // 上传文件
  async upload<T = any>(url: string, file: File, onProgress?: (progress: number) => void): Promise<ApiResponse<T>> {
    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await this.instance.post(url, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (onProgress && progressEvent.total) {
            const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total)
            onProgress(progress)
          }
        }
      })
      return response.data
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // 下载文件
  async download(url: string, filename?: string): Promise<void> {
    try {
      const response = await this.instance.get(url, {
        responseType: 'blob'
      })

      const blob = new Blob([response.data])
      const downloadUrl = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = downloadUrl
      link.download = filename || 'download'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(downloadUrl)
    } catch (error) {
      throw this.handleError(error)
    }
  }

  // 错误处理
  private handleError(error: any): Error {
    if (error.response) {
      const { status, data } = error.response
      return new Error(data.message || data.detail || `HTTP ${status} Error`)
    } else if (error.request) {
      return new Error('Network Error: Unable to connect to server')
    } else {
      return new Error(error.message || 'Unknown Error')
    }
  }

  // 设置默认头部
  setDefaultHeader(key: string, value: string): void {
    this.instance.defaults.headers.common[key] = value
  }

  // 移除默认头部
  removeDefaultHeader(key: string): void {
    delete this.instance.defaults.headers.common[key]
  }
}

// 生成请求ID
function generateRequestId() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

export default defineNuxtPlugin((nuxtApp) => {
  const apiClient = new ApiClient()

  // 将 apiClient 实例注入到 Nuxt app 上下文中
  nuxtApp.provide('api', apiClient)
})

// 类型声明
declare module '#app' {
  interface NuxtApp {
    $api: ApiClient
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $api: ApiClient
  }
}