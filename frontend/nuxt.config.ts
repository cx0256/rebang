// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devtools: { enabled: true },
  
  // 应用配置
  app: {
    head: {
      title: '热榜 - 聚合各大平台热门内容',
      meta: [
        { charset: 'utf-8' },
        { name: 'viewport', content: 'width=device-width, initial-scale=1' },
        { name: 'description', content: '热榜聚合知乎、微博、GitHub、B站等各大平台的热门内容，让你一站式了解全网热点。' },
        { name: 'keywords', content: '热榜,热搜,知乎,微博,GitHub,B站,豆瓣,热榜' },
        { name: 'author', content: 'MoMoYu Team' },
        { property: 'og:title', content: '热榜' },
        { property: 'og:description', content: '聚合各大平台热门内容' },
        { property: 'og:type', content: 'website' },
        { name: 'twitter:card', content: 'summary_large_image' }
      ],
      link: [
        { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico' },
        { rel: 'apple-touch-icon', href: '/apple-touch-icon.png' }
      ]
    }
  },
  
  // CSS 配置
  css: [
    '~/assets/css/tailwind.css',
    '~/assets/css/main.css'
  ],
  
  // 模块配置
  modules: [
    '@nuxt/ui',
    '@nuxtjs/tailwindcss',
    '@nuxtjs/color-mode',
    '@pinia/nuxt',
    '@vueuse/nuxt',
    '@nuxt/icon'
  ],
  
  // 路由规则
  routeRules: {
    '/api/**': {
      proxy: {
        to: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/**',
        // 如果后端API路径中不包含 /api，则需要重写路径
        // pathRewrite: { '^/api': '' },
      },
    },
  },

  // 运行时配置
  runtimeConfig: {
    // 私有配置（仅服务端可用）
    apiSecret: '',
    
    // 公共配置（客户端也可用）
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || '/api',
      siteUrl: process.env.NUXT_PUBLIC_SITE_URL || 'http://localhost:3000',
      gtag: process.env.NUXT_PUBLIC_GTAG || ''
    }
  },
  
  // TypeScript 配置
  typescript: {
    strict: true,
    typeCheck: true
  },
  
  // 构建配置
  build: {
    transpile: ['@headlessui/vue']
  },
  

  
  // 服务端渲染配置
  ssr: true,
  
  // 路由配置
  router: {
    options: {
      scrollBehaviorType: 'smooth'
    }
  },
  
  // 实验性功能
  experimental: {
    payloadExtraction: false
  },
  
  // Nitro 配置
  nitro: {
    preset: 'node-server',
    compressPublicAssets: true,
    prerender: {
      routes: ['/']
    },

  },
  
  // 开发服务器配置
  devServer: {
    port: 3001,
    host: 'localhost'
  },
  
  // UI 配置
  ui: {
    // 移除 colors 配置，使用默认颜色配置
    global: true
  },
  
  // 图标配置
  icon: {
    serverBundle: {
      collections: ['heroicons', 'simple-icons']
    }
  },
  
  // 颜色模式配置
  colorMode: {
    preference: 'system',
    fallback: 'light',
    hid: 'nuxt-color-mode-script',
    globalName: '__NUXT_COLOR_MODE__',
    componentName: 'ColorScheme',
    classPrefix: '',
    classSuffix: '',
    storageKey: 'nuxt-color-mode'
  },
  
  // TailwindCSS 配置
  tailwindcss: {
    cssPath: '~/assets/css/tailwind.css',
    configPath: 'tailwind.config.js'
  },
  
  // Pinia 配置
  pinia: {
    storesDirs: ['./stores/**']
  },
  
  // 自动导入配置
  imports: {
    dirs: [
      'composables',
      'utils',
      'stores'
    ]
  },
  
  // 组件自动导入
  components: {
    dirs: [
      {
        path: '~/components',
        pathPrefix: false
      }
    ]
  },
  
  // 插件配置
  plugins: [
    '~/plugins/api.client.ts',
    '~/plugins/dayjs.ts'
  ],
  

  

  
  // 兼容性配置
  compatibilityDate: '2024-01-01'
})