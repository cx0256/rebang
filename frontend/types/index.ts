// 基础类型定义
export interface BaseEntity {
  id: number
  created_at: string
  updated_at: string
}

// 平台类型
export interface Platform extends BaseEntity {
  name: string
  code: string
  display_name: string
  description?: string
  base_url: string
  icon_url?: string
  icon?: string
  is_active: boolean
  sort_order: number
  count?: number
  categories?: readonly Category[]
}

// 分类类型
export interface Category extends BaseEntity {
  platform_id: number
  code: string
  name: string
  display_name: string
  description?: string
  url: string
  parent_code?: string
  icon?: string
  is_active: boolean
  sort_order: number
  count?: number
  is_hot?: boolean
  is_new?: boolean
  platform?: Platform
  hot_items?: readonly HotItem[]
}

// 热门条目类型
export interface HotItem extends BaseEntity {
  category_id: number
  title: string
  url: string
  description?: string
  author?: string
  score?: number
  comment_count?: number
  rank?: number
  source_id?: string
  image_url?: string
  view_count?: number
  like_count?: number
  share_count?: number
  trend?: 'up' | 'down' | 'stable'
  tags?: readonly string[]
  platform?: Platform
  category?: Category
}

// 爬虫任务类型
export interface CrawlTask extends BaseEntity {
  category_id: number
  status: 'pending' | 'running' | 'completed' | 'failed'
  started_at?: string
  completed_at?: string
  item_count: number
  error_message?: string
  category?: Category
}

// 用户类型
export interface User extends BaseEntity {
  username: string
  email: string
  avatar?: string
  is_active: boolean
  is_admin: boolean
  last_login?: string
}

// 创建用户类型
export interface UserCreate {
  username: string
  email: string
  password: string
}

// API 响应类型
export interface ApiResponse<T = any> {
  success: boolean
  data?: T
  message?: string
  error?: string
}

// 分页响应类型
export interface PaginatedResponse<T = any> {
  items: T[]
  total: number
  page: number
  size: number
  pages: number
  has_next: boolean
  has_prev: boolean
}

// 分页参数类型
export interface PaginationParams {
  page?: number
  size?: number
}

// 热门条目查询参数
export interface HotItemsQuery extends PaginationParams {
  platform_id?: number
  category_id?: number
  search?: string
  sort_by?: 'created_at' | 'score' | 'comment_count' | 'rank'
  order?: 'asc' | 'desc'
  date_from?: string
  date_to?: string
}

// 统计数据类型
export interface Statistics {
  total_platforms: number
  total_categories: number
  total_hot_items: number
  total_tasks: number
  active_platforms: number
  active_categories: number
  recent_items: number
  today_updates: number
  success_rate: number
}

// 平台统计类型
export interface PlatformStats {
  platform: Platform
  total_categories: number
  total_items: number
  recent_items: number
  last_update: string
}

// 趋势数据类型
export interface TrendingItem extends HotItem {
  trend_score: number
  growth_rate: number
}

// 搜索结果类型
export interface SearchResult {
  hot_items: HotItem[]
  total: number
  query: string
  took: number
}

// 缓存状态类型
export interface CacheStatus {
  key: string
  exists: boolean
  ttl: number
  size: number
}

// 主题类型
export type Theme = 'light' | 'dark' | 'system'

// 语言类型
export type Language = 'zh-CN' | 'en-US'

// 排序选项类型
export interface SortOption {
  label: string
  value: 'created_at' | 'score' | 'comment_count' | 'rank'
  order: 'asc' | 'desc'
}

// 过滤选项类型
export interface FilterOption {
  label: string
  value: string | number
  count?: number
}

// 导航菜单类型
export interface NavItem {
  name: string
  href: string
  icon?: string
  badge?: string | number
  children?: NavItem[]
}

// 面包屑类型
export interface BreadcrumbItem {
  name: string
  href?: string
  current?: boolean
}

// 通知类型
export interface Notification {
  id: string
  type: 'success' | 'error' | 'warning' | 'info'
  title: string
  message?: string
  duration?: number
  createdAt?: number
  actions?: readonly NotificationAction[]
}

export interface NotificationAction {
  label: string
  action: () => void
  style?: 'primary' | 'secondary'
}

// 模态框类型
export interface Modal {
  id: string
  title: string
  content: string
  type?: 'info' | 'warning' | 'error' | 'success'
  confirmText?: string
  cancelText?: string
  onConfirm?: () => void
  onCancel?: () => void
}

// 表单验证规则类型
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  pattern?: RegExp
  message: string
}

// 表单字段类型
export interface FormField {
  name: string
  label: string
  type: 'text' | 'email' | 'password' | 'number' | 'select' | 'textarea'
  placeholder?: string
  options?: FilterOption[]
  rules?: ValidationRule[]
  value?: any
}

// 组件属性类型
export interface ComponentProps {
  class?: string
  style?: Record<string, any>
  [key: string]: any
}

// 事件类型
export interface CustomEvent<T = any> {
  type: string
  data?: T
  timestamp: number
}

// 错误类型
export interface AppError {
  code: string
  message: string
  details?: any
  timestamp: number
}

// 导航项类型
export interface NavigationItem {
  label: string
  to?: string
  path?: string
  href?: string
  icon?: string
  children?: NavigationItem[]
  disabled?: boolean
}

// 配置类型
export interface AppConfig {
  apiBase: string
  timeout: number
  retries: number
}

// 状态类型
export interface AppState {
  loading: boolean
  error: AppError | null
  user: User | null
  theme: Theme
  language: Language
  notifications: Notification[]
  modals: Modal[]
}