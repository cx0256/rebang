<template>
  <div id="app" class="min-h-screen app" :class="currentTheme">
    <!-- Header -->
    <header class="flex sticky top-0 z-50 justify-between items-center p-4 border-b my-header">
      <div class="flex gap-4 items-center">
        <img class="h-8 logo md:h-9" src="https://momoyu.cc/assets/logo-1-DXR4uO3F.png" alt="logo">
        <div class="relative">
          <input type="text" class="px-3 py-1.5 w-48 rounded-md md:w-64 input search" placeholder="搜索 ...">
        </div>
      </div>
      <div class="flex gap-3 items-center">
        <!-- 登录状态显示 -->
        <div v-if="!isAuthenticated" class="flex gap-2">
          <button @click="showLoginModal = true" class="px-4 py-1.5 text-sm font-semibold btn btn-green-full">登录</button>
          <button @click="showRegisterModal = true" class="px-4 py-1.5 text-sm font-semibold btn btn-blue-full">注册</button>
        </div>
        <div v-else class="flex gap-2 items-center">
          <span class="text-sm text-secondary">欢迎，{{ user?.username }}</span>
          <button @click="handleLogout" class="px-4 py-1.5 text-sm font-semibold btn btn-red-full">退出登录</button>
        </div>
        
        <button @click="toggleTheme" class="px-4 py-1.5 text-xs font-semibold text-white bg-red-600 rounded-md btn btn-red hover:bg-red-700">{{ isStealthMode ? '退出隐身' : '隐身模式' }}</button>
        <div class="sidebar-btn">
          <svg @click="toggleTheme" xmlns="http://www.w3.org/2000/svg" id="theme-toggle-icon" class="w-6 h-6 cursor-pointer" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
          </svg>
        </div>
      </div>
    </header>

    <div class="flex flex-col gap-6 mx-auto my-content lg:flex-row">
      <!-- Main Content Area -->
      <main class="grid flex-1 grid-cols-1 gap-5 content-pc md:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
        
        <!-- NGA Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #315f81;" fill="currentColor" viewBox="0 0 20 20"><path d="M10.75 3.5a.75.75 0 00-1.5 0v3.542L5.822 9.47a.75.75 0 00-.53 1.28L9.25 12.5v4.75a.75.75 0 001.5 0v-4.75l3.958-1.75a.75.75 0 00-.53-1.28L10.75 7.042V3.5z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">NGA杂谈 <span class="text-xs font-normal hot-title-time">(16分钟前)</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in ngaItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="hover:underline">{{ index + 1 }}. {{ item.title }}</a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Zhihu Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #0177d7;" fill="currentColor" viewBox="0 0 24 24"><path d="M22.083 12.61a2.122 2.122 0 0 1-1.928-2.612c.2-1.114.786-3.98 1.417-5.917C21.833 3.333 21.083 3 20.25 3h-2.5c-.5 0-1.083.25-1.417.833L15.25 5.5c-1.333.917-2.5 1.5-4.25 1.5-1.167 0-2.417-.333-3.5-1.083L6.417 5c-.167-.167-.417-.333-.75-.333H3.75c-.833 0-1.25.333-1.083 1.25.25 1.25.75 3.917 1.417 5.917.333.917 1.25 1.667 2.333 1.667.5 0 1.083-.167 1.5-.5.25-.167.417-.417.583-.667.333-.5.5-1 .583-1.417a2.84 2.84 0 0 1 1.667-1.75c1.167-.5 2.5-.75 3.75-.75s2.583.25 3.75.75a2.84 2.84 0 0 1 1.667 1.75c.083.417.25.917.583 1.417.167.25.333.5.583.667.417.333 1 .5 1.5.5.917 0 1.917-.75 2.333-1.667Z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">知乎热榜 <span class="text-xs font-normal hot-title-time">(23分钟前)</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in zhihuItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span class="flex-shrink-0 ml-2 hotness">{{ item.hot_value }}</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Tech Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #ff6b35;" fill="currentColor" viewBox="0 0 20 20"><path d="M3 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 4a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">值得买 <span class="text-xs font-normal hot-title-time">(18分钟前)</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in techItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span class="flex-shrink-0 ml-2 hotness">{{ item.hot_value }}</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- Weibo Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #e6162d;" fill="currentColor" viewBox="0 0 24 24"><path d="M9.31 8.17c-.36.36-.58.85-.58 1.4 0 1.09.89 1.98 1.98 1.98.55 0 1.04-.22 1.4-.58l2.49-2.49c.36-.36.58-.85.58-1.4 0-1.09-.89-1.98-1.98-1.98-.55 0-1.04.22-1.4.58L9.31 8.17z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">微博热搜 <span class="text-xs font-normal hot-title-time">(12分钟前)</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in weiboItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span class="flex-shrink-0 ml-2 hotness">{{ item.hot_value }}</span>
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <!-- B站热榜 Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #fb7299;" fill="currentColor" viewBox="0 0 24 24"><path d="M17.813 4.653h.854c1.51.054 2.769.578 3.773 1.574 1.004.995 1.524 2.249 1.56 3.76v7.36c-.036 1.51-.556 2.769-1.56 3.773s-2.262 1.524-3.773 1.56H5.333c-1.51-.036-2.769-.556-3.773-1.56S.036 18.858 0 17.347v-7.36c.036-1.511.556-2.765 1.56-3.76 1.004-.996 2.262-1.52 3.773-1.574h.774l-1.174-1.12a1.234 1.234 0 0 1-.373-.906c0-.356.124-.658.373-.907l.027-.027c.267-.249.573-.373.92-.373.347 0 .653.124.92.373L9.653 4.44c.071.071.134.142.187.213h4.267a.836.836 0 0 1 .16-.213l2.853-2.747c.267-.249.573-.373.92-.373.347 0 .662.151.929.4.267.249.391.551.391.907 0 .356-.124.657-.373.906l-1.174 1.12zM6.4 15.558a.928.928 0 0 0 .929.928.928.928 0 0 0 .928-.928V9.721a.928.928 0 0 0-.928-.929.928.928 0 0 0-.929.929v5.837zm4.114 0a.928.928 0 0 0 .929.928.928.928 0 0 0 .928-.928V9.721a.928.928 0 0 0-.928-.929.928.928 0 0 0-.929.929v5.837zm4.114 0a.928.928 0 0 0 .929.928.928.928 0 0 0 .929-.928V9.721a.928.928 0 0 0-.929-.929.928.928 0 0 0-.929.929v5.837z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">B站热榜 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('bilibili') }})</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in bilibiliItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span class="flex-shrink-0 ml-2 hotness">{{ item.hot_value }}</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- 今日头条 Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #ff6600;" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">今日头条 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('toutiao') }})</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in toutiaoItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span class="flex-shrink-0 ml-2 hotness">{{ item.hot_value }}</span>
                </a>
              </li>
            </ul>
          </div>
        </div>

        <!-- 虎扑步行街 Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #fe7c00;" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">虎扑步行街 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('hupu') }})</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in hupuItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="hover:underline">{{ index + 1 }}. {{ item.title }}</a>
              </li>
            </ul>
          </div>
        </div>

        <!-- IT之家 Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #d73502;" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">IT之家 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('ithome') }})</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in ithomeItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="hover:underline">{{ index + 1 }}. {{ item.title }}</a>
              </li>
            </ul>
          </div>
        </div>

        <!-- 中关村在线 Card -->
        <div class="flex flex-col rounded-lg hot-outer h-fit">
          <div class="p-4 hot-inner">
            <div class="mb-3 hot-title">
              <div class="flex justify-between items-center hot-title-inner">
                <a class="flex gap-2 items-center hot-logo" href="#">
                  <svg class="w-5 h-5" style="color: #c41e3a;" fill="currentColor" viewBox="0 0 24 24"><path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"></path></svg>
                  <span class="text-sm font-semibold hot-title-name">中关村在线 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('zol') }})</span></span>
                </a>
                <svg class="w-4 h-4 cursor-pointer" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-for="(item, index) in zolItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="hover:underline">{{ index + 1 }}. {{ item.title }}</a>
              </li>
            </ul>
          </div>
        </div>

      </main>

      <!-- Today's Hot Section - Fixed Right -->
      <aside class="flex flex-col flex-shrink-0 gap-5 w-full lg:w-72 2xl:w-80">
        <div class="flex flex-col p-4 rounded-lg side-box hot-top-box">
          <div class="flex justify-between items-center mb-4">
            <h3 class="flex gap-1.5 items-center text-base font-semibold text"><span class="text-lg">🔥</span> 今日热门</h3>
            <svg class="w-4 h-4 cursor-pointer text-secondary hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
          </div>
          <ul class="space-y-2.5 text-sm hot-content">
            <li v-for="(item, index) in todayHotItems" :key="index" class="flex justify-between items-center">
              <a href="#" @click="openLink(item.url)" class="pr-2 truncate hover:underline">{{ index + 1 }}. {{ item.title }}</a>
              <span class="flex-shrink-0 text-xs hotness">{{ item.source }}</span>
            </li>
          </ul>
        </div>

        <!-- User Info Section -->
        <div class="flex flex-col gap-5">
        <div class="p-5 rounded-lg side-box">
          <div class="flex justify-between items-center mb-4">
            <button class="flex justify-center items-center w-14 h-14 text-lg font-semibold text-white bg-blue-600 rounded-full shadow-lg avatar">读者</button>
            <div class="text-right">
              <p class="text-sm text">今天是 你关注世界的第 <span class="text-base font-bold">868</span> 天</p>
              <p class="mt-1 text-xs text-secondary">实时学习人数：<span class="font-semibold">860</span></p>
            </div>
          </div>
          <button class="py-2 w-full font-semibold text-white bg-red-600 rounded-md transition-colors hover:bg-red-700">管理订阅</button>
          <div class="flex justify-around items-center mt-4 text-secondary">
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cursor-pointer hover:text-white"><path d="M12.22 2h-4.44a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8.38"/><path d="M18 14v-4h-4v4h4zM18 10V4.5L14.5 8H18z"/></svg>
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cursor-pointer hover:text-white"><path d="M9 18V5l12-2v13"/><circle cx="6" cy="18" r="3"/><circle cx="18" cy="16" r="3"/></svg>
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cursor-pointer hover:text-white"><rect width="20" height="16" x="2" y="4" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
            <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="cursor-pointer hover:text-white"><path d="m12 8-9.04 9.06a2.82 2.82 0 1 0 3.98 3.98L16 12l3.98-3.98a2.82 2.82 0 1 0-3.98-3.98L12 8Z"/><path d="M12 12h.01"/></svg>
          </div>
        </div>

        <div class="flex flex-col p-4 rounded-lg side-box hot-top-box">
          <div class="flex justify-between items-center mb-4">
            <h3 class="flex gap-1.5 items-center text-base font-semibold text"><span class="text-lg">🔥</span> 今日热门</h3>
            <svg class="w-4 h-4 cursor-pointer text-secondary hover:text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h5M20 20v-5h-5M4 20h5v-5M20 4h-5v5"></path></svg>
          </div>
          <ul class="space-y-2.5 text-sm hot-content">
            <li v-for="(item, index) in todayHotItems" :key="index" class="flex justify-between items-center">
              <a href="#" @click="openLink(item.url)" class="pr-2 truncate hover:underline">{{ index + 1 }}. {{ item.title }}</a>
              <span class="flex-shrink-0 text-xs hotness">{{ item.source }}</span>
            </li>
          </ul>
        </div>

        <div class="p-3 text-xs leading-relaxed rounded-lg side-box tips text-secondary">
          <p class="mb-2"><a href="#" class="text-amber-400 hover:underline">🧧 领取一个外卖红包吧，每日可领取~</a></p>
          <p><span class="text-base">📣</span> 学习提醒：今天是6月23日, 周一的早上<br>学习的最高境界：所有人都以为你在偷懒，只有你知道自己在努力。<br><br>离周末还有5天</p>
        </div>
        </div>
      </aside>
    </div>

    <!-- 登录模态框 -->
    <div v-if="showLoginModal" class="flex fixed inset-0 z-50 justify-center items-center bg-black bg-opacity-50" @click.self="showLoginModal = false">
      <div class="p-6 mx-4 w-96 max-w-md rounded-lg bg-card">
        <h2 class="mb-4 text-xl font-semibold text-primary">登录</h2>
        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">用户名</label>
            <input 
              v-model="loginForm.username" 
              type="text" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="请输入用户名"
              required
            >
          </div>
          <div class="mb-6">
            <label class="block mb-2 text-sm font-medium text-secondary">密码</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="请输入密码"
              required
            >
          </div>
          <div class="flex gap-3">
            <button 
              type="submit" 
              :disabled="isLoading"
              class="flex-1 px-4 py-2 btn btn-green-full"
            >
              {{ isLoading ? '登录中...' : '登录' }}
            </button>
            <button 
              type="button" 
              @click="showLoginModal = false"
              class="flex-1 px-4 py-2 btn btn-gray"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 注册模态框 -->
    <div v-if="showRegisterModal" class="flex fixed inset-0 z-50 justify-center items-center bg-black bg-opacity-50" @click.self="showRegisterModal = false">
      <div class="p-6 mx-4 w-96 max-w-md rounded-lg bg-card">
        <h2 class="mb-4 text-xl font-semibold text-primary">注册</h2>
        <form @submit.prevent="handleRegister">
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">用户名</label>
            <input 
              v-model="registerForm.username" 
              type="text" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="请输入用户名"
              required
            >
          </div>
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">邮箱</label>
            <input 
              v-model="registerForm.email" 
              type="email" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="请输入邮箱"
              required
            >
          </div>
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">密码</label>
            <input 
              v-model="registerForm.password" 
              type="password" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="请输入密码"
              required
            >
          </div>
          <div class="mb-6">
            <label class="block mb-2 text-sm font-medium text-secondary">确认密码</label>
            <input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="请再次输入密码"
              required
            >
          </div>
          <div class="flex gap-3">
            <button 
              type="submit" 
              :disabled="isLoading"
              class="flex-1 px-4 py-2 btn btn-blue-full"
            >
              {{ isLoading ? '注册中...' : '注册' }}
            </button>
            <button 
              type="button" 
              @click="showRegisterModal = false"
              class="flex-1 px-4 py-2 btn btn-gray"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 通知容器 -->
    <NotificationContainer />

  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'

// 认证相关
const { isAuthenticated, user, login, register, logout } = useAuth()
const { addNotification } = useNotification()

// 模态框状态
const showLoginModal = ref(false)
const showRegisterModal = ref(false)

// 登录表单
const loginForm = ref({
  username: '',
  password: ''
})

// 注册表单
const registerForm = ref({
  username: '',
  email: '',
  password: '',
  confirmPassword: ''
})

// 加载状态
const isLoading = ref(false)

// 主题状态
const isStealthMode = ref(false)
const currentTheme = computed(() => isStealthMode.value ? 'theme-stealth' : 'theme-1')

// 主题切换函数
const toggleTheme = () => {
  isStealthMode.value = !isStealthMode.value
}

// 处理登录
const handleLogin = async () => {
  if (!loginForm.value.username || !loginForm.value.password) {
    addNotification('error', '请填写用户名和密码')
    return
  }

  isLoading.value = true
  try {
    const result = await login(loginForm.value)
    if (result.success) {
      addNotification('success', '登录成功')
      showLoginModal.value = false
      loginForm.value = { username: '', password: '' }
    } else {
      addNotification('error', result.error || '登录失败')
    }
  } finally {
    isLoading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    addNotification('error', '请填写所有必填字段')
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    addNotification('error', '密码确认不匹配')
    return
  }

  isLoading.value = true
  try {
    const result = await register(registerForm.value)
    if (result.success) {
      addNotification('success', '注册成功，请登录')
      showRegisterModal.value = false
      registerForm.value = { username: '', email: '', password: '', confirmPassword: '' }
    } else {
      addNotification('error', result.error || '注册失败')
    }
  } finally {
    isLoading.value = false
  }
}

// 处理登出
const handleLogout = async () => {
  try {
    await logout()
    addNotification('success', '已退出登录')
  } catch (error) {
    addNotification('error', '退出登录失败')
  }
}

// 定义热榜项目类型
interface HotItem {
  title: string
  url: string
  hot_value?: string | number
  rank?: number
  source?: string
}

// 热榜数据状态
const ngaItems = ref<HotItem[]>([])
const zhihuItems = ref<HotItem[]>([])
const techItems = ref<HotItem[]>([])
const weiboItems = ref<HotItem[]>([])
const bilibiliItems = ref<HotItem[]>([])
const toutiaoItems = ref<HotItem[]>([])
const hupuItems = ref<HotItem[]>([])
const ithomeItems = ref<HotItem[]>([])
const zolItems = ref<HotItem[]>([])
const todayHotItems = ref<HotItem[]>([])

// 数据更新时间
const lastUpdateTimes = ref<Record<string, Date>>({})

// 定义API响应类型
interface ApiResponse {
  success: boolean
  data: {
    items: {
      title: string
      url: string
      platform_name: string
      hot_value: string | number
      rank: number
    }[]
  }
}

// API调用函数
const fetchHotItems = async () => {
  try {
    const config = useRuntimeConfig()
    const response = await $fetch<ApiResponse>('/api/v1/hot/', {
      baseURL: config.public.apiBase,
      query: {
        hours: 24,
        size: 30
      }
    })
    
    if (response.success && response.data) {
      // 按平台分组数据
      const groupedData: Record<string, HotItem[]> = {}
      response.data.items.forEach((item) => {
        const platform = item.platform_name
        if (!groupedData[platform]) {
          groupedData[platform] = []
        }
        groupedData[platform].push({
          title: item.title,
          url: item.url,
          hot_value: item.hot_value,
          rank: item.rank
        })
      })
      
      // 更新各平台数据
      ngaItems.value = groupedData['NGA'] || []
      zhihuItems.value = groupedData['知乎'] || []
      weiboItems.value = groupedData['微博'] || []
      bilibiliItems.value = groupedData['B站'] || []
      toutiaoItems.value = groupedData['今日头条'] || []
      hupuItems.value = groupedData['虎扑'] || []
      ithomeItems.value = groupedData['IT之家'] || []
      zolItems.value = groupedData['中关村在线'] || []
      
      // 更新时间戳
      const now = new Date()
      Object.keys(groupedData).forEach(platform => {
        lastUpdateTimes.value[platform.toLowerCase()] = now
      })
      
      // 生成今日热门（取各平台前几条）
      const allItems: HotItem[] = []
      Object.entries(groupedData).forEach(([platform, items]) => {
        items.slice(0, 2).forEach((item: HotItem) => {
          allItems.push({
            ...item,
            source: platform
          })
        })
      })
      todayHotItems.value = allItems.slice(0, 10)
    }
  } catch (error) {
    console.error('获取热榜数据失败:', error)
    // 如果API调用失败，使用默认数据
    loadDefaultData()
  }
}

// 默认数据（API调用失败时使用）
const loadDefaultData = () => {
  ngaItems.value = [
    { title: '客户端闪退问题，请下载恩基爱社区app。', url: '#' },
    { title: '假设：伊朗封锁霍尔木兹海峡...', url: '#' },
    { title: '汪峰找的女友都挺漂亮', url: '#' }
  ]
  zhihuItems.value = [
    { title: '延边大学毕业典礼上，首都网络的发言台', hot_value: '402 万', url: '#' },
    { title: '滴滴打车为什么总派远处的车...', hot_value: '321 万', url: '#' }
  ]
  weiboItems.value = [
    { title: '全世界历史摸鱼党的热门', hot_value: '1148442', url: '#' },
    { title: '网络网络收取题目一功能性160万元', hot_value: '721515', url: '#' }
  ]
}

// 获取时间差显示函数
const getTimeAgo = (platform: string) => {
  const lastUpdate = lastUpdateTimes.value[platform]
  if (!lastUpdate) return '未知'
  
  const now = new Date()
  const diff = Math.floor((now.getTime() - lastUpdate.getTime()) / (1000 * 60))
  
  if (diff < 1) return '刚刚'
  if (diff < 60) return `${diff}分钟前`
  if (diff < 1440) return `${Math.floor(diff / 60)}小时前`
  return `${Math.floor(diff / 1440)}天前`
}

// 打开链接函数
const openLink = (url: string) => {
  if (url && url !== '#') {
    window.open(url, '_blank')
  }
}

// 页面加载时获取数据
onMounted(() => {
  fetchHotItems()
  // 每5分钟刷新一次数据
  setInterval(fetchHotItems, 5 * 60 * 1000)
})

// 页面元数据
useHead({
  title: '热榜 - 聚合全网热点资讯',
  meta: [
    { name: 'description', content: '热榜 - 聚合NGA、知乎、微博等平台热点资讯，一站式浏览全网热门内容' },
    { name: 'keywords', content: '摸鱼,热榜,NGA,知乎,微博,热点资讯,聚合' }
  ]
})
</script>

<style>
/* 全局样式变量 - 移除scoped以确保CSS变量全局可用 */
:root {
  /* 默认主题变量 */
  --bg-primary: #1a1a1a;
  --bg-secondary: #2a2a2a;
  --bg-card: #2d2d2d;
  --text-primary: #e5e5e5;
  --text-secondary: #a0a0a0;
  --text-muted: #666;
  --border-color: #404040;
  --icon-color: #888;
}

.app {
  background: var(--bg-primary, #1a1a1a);
  color: var(--text-primary, #e5e5e5);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 主题样式 */
.theme-1 {
  --bg-primary: #1a1a1a;
  --bg-secondary: #2a2a2a;
  --bg-card: #2d2d2d;
  --text-primary: #e5e5e5;
  --text-secondary: #a0a0a0;
  --text-muted: #666;
  --border-color: #404040;
  --icon-color: #888;
}

.theme-stealth {
  --bg-primary: #0f0f0f;
  --bg-secondary: #1a1a1a;
  --bg-card: #1f1f1f;
  --text-primary: #d0d0d0;
  --text-secondary: #888;
  --text-muted: #555;
  --border-color: #333;
  --icon-color: #666;
}

/* 头部样式 */
.my-header {
  background: var(--bg-secondary, #2a2a2a);
  border-color: var(--border-color, #404040);
}

.logo {
  filter: brightness(1.2);
}

.input {
  background: var(--bg-card, #2d2d2d);
  border: 1px solid var(--border-color, #404040);
  color: var(--text-primary, #e5e5e5);
  transition: border-color 0.2s ease;
}

.input:focus {
  outline: none;
  border-color: #4f46e5;
}

.input::placeholder {
  color: var(--text-muted, #666);
}

/* 按钮样式 */
.btn {
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
  transition: all 0.2s ease;
  text-align: center;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-green-full {
  background: #10b981;
  color: white;
}

.btn-green-full:hover:not(:disabled) {
  background: #059669;
}

.btn-blue-full {
  background: #3b82f6;
  color: white;
}

.btn-blue-full:hover:not(:disabled) {
  background: #2563eb;
}

.btn-red-full {
  background: #ef4444;
  color: white;
}

.btn-red-full:hover:not(:disabled) {
  background: #dc2626;
}

.btn-gray {
  background: var(--bg-card, #2d2d2d);
  color: var(--text-secondary, #a0a0a0);
  border: 1px solid var(--border-color, #404040);
}

.btn-gray:hover:not(:disabled) {
  background: var(--bg-secondary, #2a2a2a);
  color: var(--text-primary, #e5e5e5);
}

/* 模态框样式 */
.bg-card {
  background: var(--bg-card, #2d2d2d);
  border: 1px solid var(--border-color, #404040);
}

.text-primary {
  color: var(--text-primary, #e5e5e5);
}

.text-secondary {
  color: var(--text-secondary, #a0a0a0);
}

/* 卡片样式 */
.hot-outer {
  background: var(--bg-card, #2d2d2d);
  border: 1px solid var(--border-color, #404040);
  transition: all 0.2s ease;
}

.hot-outer:hover {
  border-color: #555;
  transform: translateY(-1px);
}

.hot-inner {
  color: var(--text-primary, #e5e5e5);
}

.hot-title-name {
  color: var(--text-primary, #e5e5e5);
  font-size: 14px;
}

.hot-title-time {
  color: var(--text-secondary, #a0a0a0);
  font-size: 12px;
}

.hot-content li {
  border-bottom: 1px solid transparent;
  padding-bottom: 8px;
  margin-bottom: 8px;
}

.hot-content li:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.hot-content a {
  color: var(--text-primary, #e5e5e5);
  text-decoration: none;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  line-height: 1.4;
}

.hot-content a:hover {
  color: #60a5fa;
}

.hotness {
  color: var(--text-secondary, #a0a0a0);
  font-size: 11px;
  margin-left: 8px;
  flex-shrink: 0;
}

/* 侧边栏样式 */
.side-box {
  background: var(--bg-card, #2d2d2d);
  border: 1px solid var(--border-color, #404040);
}

.avatar {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.text {
  color: var(--text-primary, #e5e5e5);
}

.text-secondary {
  color: var(--text-secondary, #a0a0a0);
}

/* 按钮样式 */
.btn-red {
  background: #dc2626;
  transition: background-color 0.2s ease;
}

.btn-red:hover {
  background: #b91c1c;
}

/* 基础内容样式 */
.my-content {
  padding: 20px;
  gap: 20px;
  max-width: 100vw;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .my-content {
    padding: 12px;
    gap: 12px;
  }
  .hot-inner {
    padding: 12px;
  }
}

/* 大屏模式优化 */
@media (min-width: 769px) {
  .my-content {
    padding: 2vw;
    gap: 24px;
  }
}

@media (min-width: 1920px) {
  .my-content {
    padding: 1.5vw;
    gap: 24px;
  }
}

/* 网格布局优化 - 最大5列自适应 */
.content-pc {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

@media (min-width: 768px) {
  .content-pc {
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  }
}

@media (min-width: 1024px) {
  .content-pc {
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  }
}

@media (min-width: 1280px) {
  .content-pc {
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  }
}

@media (min-width: 1536px) {
  .content-pc {
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  }
}

/* 限制最大4列（加上右侧栏总共5列） */
@media (min-width: 1920px) {
  .content-pc {
    grid-template-columns: repeat(4, 1fr);
    max-width: calc(100% - 320px); /* 为右侧栏预留空间 */
  }
}

/* 页脚样式 */
.my-footer {
  background: var(--bg-secondary, #2a2a2a);
  border-top: 1px solid var(--border-color, #404040);
  color: var(--text-muted, #666);
}

.my-footer a {
  color: var(--text-secondary, #a0a0a0);
  transition: color 0.2s ease;
}

.my-footer a:hover {
  color: var(--text-primary, #e5e5e5);
}

/* 滚动条样式 */
::-webkit-scrollbar {
  width: 6px;
}

::-webkit-scrollbar-track {
  background: var(--bg-primary, #1a1a1a);
}

::-webkit-scrollbar-thumb {
  background: var(--border-color, #404040);
  border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
  background: #555;
}
</style>