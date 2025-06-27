import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import utc from 'dayjs/plugin/utc'
import timezone from 'dayjs/plugin/timezone'
import duration from 'dayjs/plugin/duration'
import isToday from 'dayjs/plugin/isToday'
import isYesterday from 'dayjs/plugin/isYesterday'
import isTomorrow from 'dayjs/plugin/isTomorrow'
import weekOfYear from 'dayjs/plugin/weekOfYear'
import quarterOfYear from 'dayjs/plugin/quarterOfYear'
import 'dayjs/locale/zh-cn'

export default defineNuxtPlugin(() => {
  // 扩展dayjs插件
  dayjs.extend(relativeTime)
  dayjs.extend(utc)
  dayjs.extend(timezone)
  dayjs.extend(duration)
  dayjs.extend(isToday)
  dayjs.extend(isYesterday)
  dayjs.extend(isTomorrow)
  dayjs.extend(weekOfYear)
  dayjs.extend(quarterOfYear)

  // 设置默认语言为中文
  dayjs.locale('zh-cn')

  // 设置默认时区
  dayjs.tz.setDefault('Asia/Shanghai')

  // 自定义格式化函数
  const formatters = {
    // 标准日期时间格式
    datetime: (date: string | Date | dayjs.Dayjs) => {
      return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
    },

    // 日期格式
    date: (date: string | Date | dayjs.Dayjs) => {
      return dayjs(date).format('YYYY-MM-DD')
    },

    // 时间格式
    time: (date: string | Date | dayjs.Dayjs) => {
      return dayjs(date).format('HH:mm:ss')
    },

    // 相对时间（如：2小时前）
    relative: (date: string | Date | dayjs.Dayjs) => {
      const target = dayjs(date)
      const now = dayjs()
      const diff = now.diff(target, 'minute')

      if (diff < 1) {
        return '刚刚'
      } else if (diff < 60) {
        return `${diff}分钟前`
      } else if (diff < 1440) {
        return `${Math.floor(diff / 60)}小时前`
      } else if (diff < 10080) {
        return `${Math.floor(diff / 1440)}天前`
      } else {
        return target.format('YYYY-MM-DD')
      }
    },

    // 智能格式化（根据时间距离选择合适格式）
    smart: (date: string | Date | dayjs.Dayjs) => {
      const target = dayjs(date)
      const now = dayjs()

      if (target.isToday()) {
        return `今天 ${target.format('HH:mm')}`
      } else if (target.isYesterday()) {
        return `昨天 ${target.format('HH:mm')}`
      } else if (target.isTomorrow()) {
        return `明天 ${target.format('HH:mm')}`
      } else if (now.diff(target, 'day') < 7) {
        const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
        return `${weekdays[target.day()]} ${target.format('HH:mm')}`
      } else if (target.year() === now.year()) {
        return target.format('MM-DD HH:mm')
      } else {
        return target.format('YYYY-MM-DD')
      }
    },

    // 友好的日期格式
    friendly: (date: string | Date | dayjs.Dayjs) => {
      const target = dayjs(date)
      const now = dayjs()
      const diffDays = now.diff(target, 'day')

      if (target.isToday()) {
        return '今天'
      } else if (target.isYesterday()) {
        return '昨天'
      } else if (target.isTomorrow()) {
        return '明天'
      } else if (diffDays > 0 && diffDays < 7) {
        return `${diffDays}天前`
      } else if (diffDays < 0 && diffDays > -7) {
        return `${Math.abs(diffDays)}天后`
      } else {
        return target.format('YYYY年MM月DD日')
      }
    },

    // 持续时间格式化
    duration: (seconds: number) => {
      const dur = dayjs.duration(seconds, 'seconds')
      const hours = Math.floor(dur.asHours())
      const minutes = dur.minutes()
      const secs = dur.seconds()

      if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
      } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`
      }
    },

    // 文件大小友好格式
    fileSize: (bytes: number) => {
      const sizes = ['B', 'KB', 'MB', 'GB', 'TB']
      if (bytes === 0) return '0 B'
      const i = Math.floor(Math.log(bytes) / Math.log(1024))
      return `${Math.round(bytes / Math.pow(1024, i) * 100) / 100} ${sizes[i]}`
    },

    // 数字友好格式
    number: (num: number) => {
      if (num >= 1000000) {
        return `${Math.round(num / 100000) / 10}M`
      } else if (num >= 1000) {
        return `${Math.round(num / 100) / 10}K`
      } else {
        return num.toString()
      }
    }
  }

  // 工具函数
  const utils = {
    // 获取时间范围
    getTimeRange: (type: 'today' | 'yesterday' | 'week' | 'month' | 'year') => {
      const now = dayjs()
      let start: dayjs.Dayjs
      let end: dayjs.Dayjs

      switch (type) {
        case 'today':
          start = now.startOf('day')
          end = now.endOf('day')
          break
        case 'yesterday':
          start = now.subtract(1, 'day').startOf('day')
          end = now.subtract(1, 'day').endOf('day')
          break
        case 'week':
          start = now.startOf('week')
          end = now.endOf('week')
          break
        case 'month':
          start = now.startOf('month')
          end = now.endOf('month')
          break
        case 'year':
          start = now.startOf('year')
          end = now.endOf('year')
          break
        default:
          start = now.startOf('day')
          end = now.endOf('day')
      }

      return {
        start: start.toISOString(),
        end: end.toISOString(),
        startFormat: start.format('YYYY-MM-DD HH:mm:ss'),
        endFormat: end.format('YYYY-MM-DD HH:mm:ss')
      }
    },

    // 判断是否为工作日
    isWorkday: (date: string | Date | dayjs.Dayjs) => {
      const day = dayjs(date).day()
      return day >= 1 && day <= 5
    },

    // 获取下一个工作日
    getNextWorkday: (date?: string | Date | dayjs.Dayjs) => {
      let current = date ? dayjs(date) : dayjs()
      do {
        current = current.add(1, 'day')
      } while (!utils.isWorkday(current))
      return current
    },

    // 计算年龄
    getAge: (birthDate: string | Date | dayjs.Dayjs) => {
      return dayjs().diff(dayjs(birthDate), 'year')
    },

    // 获取季度
    getQuarter: (date?: string | Date | dayjs.Dayjs) => {
      return dayjs(date).quarter()
    },

    // 获取周数
    getWeekOfYear: (date?: string | Date | dayjs.Dayjs) => {
      return dayjs(date).week()
    },

    // 时间验证
    isValid: (date: string | Date | dayjs.Dayjs) => {
      return dayjs(date).isValid()
    },

    // 时间比较
    compare: (date1: string | Date | dayjs.Dayjs, date2: string | Date | dayjs.Dayjs) => {
      const d1 = dayjs(date1)
      const d2 = dayjs(date2)
      if (d1.isBefore(d2)) return -1
      if (d1.isAfter(d2)) return 1
      return 0
    }
  }

  // 提供全局实例
  return {
    provide: {
      formatTime: formatters,
      timeUtils: utils
    }
  }
})

// 类型声明
type FormattersType = {
  datetime: (date: string | Date | dayjs.Dayjs) => string
  date: (date: string | Date | dayjs.Dayjs) => string
  time: (date: string | Date | dayjs.Dayjs) => string
  relative: (date: string | Date | dayjs.Dayjs) => string
  smart: (date: string | Date | dayjs.Dayjs) => string
  friendly: (date: string | Date | dayjs.Dayjs) => string
  calendar: (date: string | Date | dayjs.Dayjs) => string
  duration: (start: string | Date | dayjs.Dayjs, end: string | Date | dayjs.Dayjs) => string
  countdown: (target: string | Date | dayjs.Dayjs) => string
  timeAgo: (date: string | Date | dayjs.Dayjs) => string
  timeUntil: (date: string | Date | dayjs.Dayjs) => string
  shortDate: (date: string | Date | dayjs.Dayjs) => string
  longDate: (date: string | Date | dayjs.Dayjs) => string
  monthYear: (date: string | Date | dayjs.Dayjs) => string
  yearOnly: (date: string | Date | dayjs.Dayjs) => string
}

type UtilsType = {
  startOfDay: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  endOfDay: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  startOfWeek: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  endOfWeek: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  startOfMonth: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  endOfMonth: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  startOfYear: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  endOfYear: (date?: string | Date | dayjs.Dayjs) => dayjs.Dayjs
  addDays: (date: string | Date | dayjs.Dayjs, days: number) => dayjs.Dayjs
  addWeeks: (date: string | Date | dayjs.Dayjs, weeks: number) => dayjs.Dayjs
  addMonths: (date: string | Date | dayjs.Dayjs, months: number) => dayjs.Dayjs
  addYears: (date: string | Date | dayjs.Dayjs, years: number) => dayjs.Dayjs
  subtractDays: (date: string | Date | dayjs.Dayjs, days: number) => dayjs.Dayjs
  subtractWeeks: (date: string | Date | dayjs.Dayjs, weeks: number) => dayjs.Dayjs
  subtractMonths: (date: string | Date | dayjs.Dayjs, months: number) => dayjs.Dayjs
  subtractYears: (date: string | Date | dayjs.Dayjs, years: number) => dayjs.Dayjs
  getDaysInMonth: (date?: string | Date | dayjs.Dayjs) => number
  getDayOfWeek: (date?: string | Date | dayjs.Dayjs) => number
  getDayOfYear: (date?: string | Date | dayjs.Dayjs) => number
  getWeeksInYear: (date?: string | Date | dayjs.Dayjs) => number
  isLeapYear: (date?: string | Date | dayjs.Dayjs) => boolean
  isSameDay: (date1: string | Date | dayjs.Dayjs, date2: string | Date | dayjs.Dayjs) => boolean
  isSameWeek: (date1: string | Date | dayjs.Dayjs, date2: string | Date | dayjs.Dayjs) => boolean
  isSameMonth: (date1: string | Date | dayjs.Dayjs, date2: string | Date | dayjs.Dayjs) => boolean
  isSameYear: (date1: string | Date | dayjs.Dayjs, date2: string | Date | dayjs.Dayjs) => boolean
  isWeekend: (date?: string | Date | dayjs.Dayjs) => boolean
  isWorkday: (date?: string | Date | dayjs.Dayjs) => boolean
  getBusinessDays: (start: string | Date | dayjs.Dayjs, end: string | Date | dayjs.Dayjs) => number
  getAge: (birthDate: string | Date | dayjs.Dayjs) => number
  getQuarter: (date?: string | Date | dayjs.Dayjs) => number
  getWeekOfYear: (date?: string | Date | dayjs.Dayjs) => number
  isValid: (date: string | Date | dayjs.Dayjs) => boolean
  compare: (date1: string | Date | dayjs.Dayjs, date2: string | Date | dayjs.Dayjs) => number
}

declare module '#app' {
  interface NuxtApp {
    $dayjs: typeof dayjs
    $formatTime: FormattersType
    $timeUtils: UtilsType
  }
}

declare module 'vue' {
  interface ComponentCustomProperties {
    $dayjs: typeof dayjs
    $formatTime: FormattersType
    $timeUtils: UtilsType
  }
}