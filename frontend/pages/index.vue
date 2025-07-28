<template>
  <div id="app" class="min-h-screen app" :class="currentTheme">
    <!-- Header -->
    <header class="flex sticky top-0 z-50 justify-between items-center p-4 border-b my-header">
      <div class="flex gap-4 items-center">
        <img class="h-8 logo md:h-9" src="https://momoyu.cc/assets/logo-1-DXR4uO3F.png" alt="logo">
        <div class="relative search-container">
          <input v-model="searchQuery" @input="handleSearch" type="text" class="px-3 py-1.5 w-48 rounded-md md:w-64 input search" placeholder="Search hot topics...">
          <div v-if="searchResults.length > 0" class="overflow-y-auto absolute right-0 left-0 top-full z-50 mt-1 max-h-60 rounded-md border border-gray-600 shadow-lg bg-card">
            <div v-for="(result, index) in searchResults" :key="index" @click="selectSearchResult(result.url)" class="px-3 py-2 border-b border-gray-600 cursor-pointer hover:bg-gray-700 last:border-b-0">
              <div class="text-sm text-primary">{{ result.title }}</div>
              <div class="text-xs text-secondary">{{ result.source }}</div>
            </div>
          </div>
        </div>
      </div>
      <div class="flex gap-3 items-center">
        <!-- 登录状态显示 -->
        <div v-if="!isAuthenticated" class="flex gap-2">
          <button @click="showLoginModal = true" class="px-4 py-1.5 text-sm font-semibold btn btn-green-full">Login</button>
          <button @click="showRegisterModal = true" class="px-4 py-1.5 text-sm font-semibold btn btn-blue-full">Register</button>
        </div>
        <div v-else class="flex gap-2 items-center">
          <span class="text-sm text-secondary">Welcome, {{ user?.username }}</span>
          <button @click="handleLogout" class="px-4 py-1.5 text-sm font-semibold btn btn-red-full">Logout</button>
        </div>
        
        <div class="sidebar-btn">
          <svg @click="toggleDarkMode" xmlns="http://www.w3.org/2000/svg" id="theme-toggle-icon" class="w-6 h-6 transition-transform cursor-pointer hover:scale-110" :class="isDarkMode ? 'text-yellow-400' : 'text-gray-400'" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path v-if="!isDarkMode" stroke-linecap="round" stroke-linejoin="round" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
            <path v-else stroke-linecap="round" stroke-linejoin="round" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
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
                  <span class="text-sm font-semibold hot-title-name">NGA杂谈 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('nga') }})</span></span>
                </a>
                <button @click="refreshPlatformData('nga')" :disabled="refreshingPlatforms.nga" class="p-1.5 rounded-full transition-all hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" :title="refreshingPlatforms.nga ? 'Refreshing...' : 'Refresh NGA data'">
                  <svg class="w-4 h-4" :class="{ 'animate-spin text-blue-400': refreshingPlatforms.nga }" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-if="ngaItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
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
                  <span class="text-sm font-semibold hot-title-name">知乎热榜 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('zhihu') }})</span></span>
                </a>
                <button @click="refreshPlatformData('zhihu')" :disabled="refreshingPlatforms.zhihu" class="p-1.5 rounded-full transition-all hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" :title="refreshingPlatforms.zhihu ? 'Refreshing...' : 'Refresh Zhihu data'">
                  <svg class="w-4 h-4" :class="{ 'animate-spin text-blue-400': refreshingPlatforms.zhihu }" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-if="zhihuItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
              <li v-for="(item, index) in zhihuItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span v-if="formatHotValue(item.hot_value)" class="flex-shrink-0 ml-2 hotness">{{ formatHotValue(item.hot_value) }}</span>
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
                  <span class="text-sm font-semibold hot-title-name">值得买 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('smzdm') }})</span></span>
                </a>
                <button @click="refreshPlatformData('smzdm')" :disabled="refreshingPlatforms.smzdm" class="p-1.5 rounded-full transition-all hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" :title="refreshingPlatforms.smzdm ? 'Refreshing...' : 'Refresh SMZDM data'">
                  <svg class="w-4 h-4" :class="{ 'animate-spin text-blue-400': refreshingPlatforms.smzdm }" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-if="techItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
              <li v-for="(item, index) in techItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span v-if="formatHotValue(item.hot_value)" class="flex-shrink-0 ml-2 hotness">{{ formatHotValue(item.hot_value) }}</span>
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
                  <span class="text-sm font-semibold hot-title-name">微博热搜 <span class="text-xs font-normal hot-title-time">({{ getTimeAgo('weibo') }})</span></span>
                </a>
                <button @click="refreshPlatformData('weibo')" :disabled="refreshingPlatforms.weibo" class="p-1.5 rounded-full transition-all hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" :title="refreshingPlatforms.weibo ? 'Refreshing...' : 'Refresh Weibo data'">
                  <svg class="w-4 h-4" :class="{ 'animate-spin text-blue-400': refreshingPlatforms.weibo }" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-if="weiboItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
              <li v-for="(item, index) in weiboItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span v-if="formatHotValue(item.hot_value)" class="flex-shrink-0 ml-2 hotness">{{ formatHotValue(item.hot_value) }}</span>
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
                <button @click="refreshPlatformData('bilibili')" :disabled="refreshingPlatforms.bilibili" class="p-1.5 rounded-full transition-all hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" :title="refreshingPlatforms.bilibili ? 'Refreshing...' : 'Refresh Bilibili data'">
                  <svg class="w-4 h-4" :class="{ 'animate-spin text-blue-400': refreshingPlatforms.bilibili }" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-if="bilibiliItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
              <li v-for="(item, index) in bilibiliItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span v-if="formatHotValue(item.hot_value)" class="flex-shrink-0 ml-2 hotness">{{ formatHotValue(item.hot_value) }}</span>
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
                <button @click="refreshPlatformData('toutiao')" :disabled="refreshingPlatforms.toutiao" class="p-1.5 rounded-full transition-all hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" :title="refreshingPlatforms.toutiao ? 'Refreshing...' : 'Refresh Toutiao data'">
                  <svg class="w-4 h-4" :class="{ 'animate-spin text-blue-400': refreshingPlatforms.toutiao }" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-if="toutiaoItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
              <li v-for="(item, index) in toutiaoItems" :key="index">
                <a href="#" @click="openLink(item.url)" class="flex justify-between hover:underline">
                  <span>{{ index + 1 }}. {{ item.title }}</span> 
                  <span v-if="formatHotValue(item.hot_value)" class="flex-shrink-0 ml-2 hotness">{{ formatHotValue(item.hot_value) }}</span>
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
                <button @click="refreshPlatformData('hupu')" :disabled="refreshingPlatforms.hupu" class="p-1.5 rounded-full transition-all hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed" :title="refreshingPlatforms.hupu ? 'Refreshing...' : 'Refresh Hupu data'">
                  <svg class="w-4 h-4" :class="{ 'animate-spin text-blue-400': refreshingPlatforms.hupu }" style="color:var(--icon-color);" fill="none" stroke="currentColor" viewBox="0 0 24 24" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
            </div>
            <ul class="space-y-2.5 text-sm hot-content">
              <li v-if="hupuItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
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
              <li v-if="ithomeItems.length === 0" class="py-4 text-center text-gray-500">
                <div class="text-xs">暂无数据</div>
              </li>
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
      <aside class="flex flex-col flex-shrink-0 gap-5 w-full lg:w-72 2xl:w-80 lg:sticky lg:top-5 lg:self-start lg:max-h-screen lg:overflow-y-auto">

        <!-- User Info Section -->
        <div class="flex flex-col gap-5">
        <div class="p-5 rounded-lg side-box">
          <div v-if="isAuthenticated" class="flex justify-between items-center mb-4">
            <button class="flex justify-center items-center w-14 h-14 text-lg font-semibold text-white bg-blue-600 rounded-full shadow-lg avatar">
              {{ user?.username?.charAt(0).toUpperCase() || 'U' }}
            </button>
            <div class="text-right">
              <p class="text-sm text">Welcome back, <span class="text-base font-bold">{{ user?.username }}</span></p>
              <p class="mt-1 text-xs text-secondary">Last login: <span class="font-semibold">{{ user?.last_login ? new Date(user.last_login).toLocaleDateString() : 'Today' }}</span></p>
            </div>
          </div>
          <div v-else class="flex justify-between items-center mb-4">
            <button class="flex justify-center items-center w-14 h-14 text-lg font-semibold text-white bg-gray-600 rounded-full shadow-lg avatar">Guest</button>
            <div class="text-right">
              <p class="text-sm text">Welcome to <span class="text-base font-bold">Hot Topics</span></p>
              <p class="mt-1 text-xs text-secondary">Please login to save preferences</p>
            </div>
          </div>
          <div v-if="isAuthenticated" class="text-center">
            <p class="text-sm text-green-400">✓ Account Status: Active</p>
            <p class="text-xs text-secondary mt-1">Preferences saved automatically</p>
          </div>
          <div v-else class="text-center">
            <p class="text-sm text-yellow-400">⚠ Guest Mode</p>
            <p class="text-xs text-secondary mt-1">Login to save your preferences</p>
          </div>
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
        <h2 class="mb-4 text-xl font-semibold text-primary">Login</h2>
        
        <!-- 错误信息显示 -->
        <div v-if="loginError" class="mb-4 p-3 text-sm text-red-400 bg-red-900/20 border border-red-500/30 rounded-md">
          {{ loginError }}
        </div>
        
        <form @submit.prevent="handleLogin">
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">Username</label>
            <input 
              v-model="loginForm.username" 
              type="text" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="Enter your username"
              required
            >
          </div>
          <div class="mb-6">
            <label class="block mb-2 text-sm font-medium text-secondary">Password</label>
            <input 
              v-model="loginForm.password" 
              type="password" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="Enter your password"
              required
            >
          </div>
          <div class="flex gap-3">
            <button 
              type="submit" 
              :disabled="isLoading"
              class="flex-1 px-4 py-2 btn btn-green-full"
            >
              {{ isLoading ? 'Logging in...' : 'Login' }}
            </button>
            <button 
              type="button" 
              @click="showLoginModal = false; loginError = ''"
              class="flex-1 px-4 py-2 btn btn-gray"
            >
              Cancel
            </button>
          </div>
        </form>
      </div>
    </div>

    <!-- 注册模态框 -->
    <div v-if="showRegisterModal" class="flex fixed inset-0 z-50 justify-center items-center bg-black bg-opacity-50" @click.self="showRegisterModal = false">
      <div class="p-6 mx-4 w-96 max-w-md rounded-lg bg-card">
        <h2 class="mb-4 text-xl font-semibold text-primary">Register</h2>
        
        <!-- 错误信息显示 -->
        <div v-if="registerError" class="mb-4 p-3 text-sm text-red-400 bg-red-900/20 border border-red-500/30 rounded-md">
          {{ registerError }}
        </div>
        
        <form @submit.prevent="handleRegister">
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">Username</label>
            <input 
              v-model="registerForm.username" 
              type="text" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="Enter your username"
              required
            >
          </div>
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">Email</label>
            <input 
              v-model="registerForm.email" 
              type="email" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="Enter your email"
              required
            >
          </div>
          <div class="mb-4">
            <label class="block mb-2 text-sm font-medium text-secondary">Password</label>
            <input 
              v-model="registerForm.password" 
              type="password" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="Enter your password"
              required
            >
          </div>
          <div class="mb-6">
            <label class="block mb-2 text-sm font-medium text-secondary">Confirm Password</label>
            <input 
              v-model="registerForm.confirmPassword" 
              type="password" 
              class="px-3 py-2 w-full rounded-md input" 
              placeholder="Confirm your password"
              required
            >
          </div>
          <div class="flex gap-3">
            <button 
              type="submit" 
              :disabled="isLoading"
              class="flex-1 px-4 py-2 btn btn-blue-full"
            >
              {{ isLoading ? 'Registering...' : 'Register' }}
            </button>
            <button 
              type="button" 
              @click="showRegisterModal = false; registerError = ''"
              class="flex-1 px-4 py-2 btn btn-gray"
            >
              Cancel
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
import { computed, onMounted, ref, watch } from 'vue'

// 认证相关
const { isAuthenticated, user, login, register, logout, initAuth } = useAuth()
const { addNotification } = useNotification()

// 用户配置状态
const userConfig = ref({
  theme: 'dark',
  language: 'zh-CN',
  autoRefresh: true,
  refreshInterval: 5,
  showHotValues: true,
  compactMode: false
})

// 保存用户配置到localStorage
const saveUserConfig = () => {
  if (process.client) {
    localStorage.setItem('userConfig', JSON.stringify(userConfig.value))
  }
}

// 加载用户配置
const loadUserConfig = () => {
  if (process.client) {
    const saved = localStorage.getItem('userConfig')
    if (saved) {
      try {
        userConfig.value = { ...userConfig.value, ...JSON.parse(saved) }
      } catch (error) {
        console.error('Failed to load user config:', error)
      }
    }
  }
}

// 监听配置变化并自动保存
watch(userConfig, saveUserConfig, { deep: true })

// 模态框状态
const showLoginModal = ref(false)
const showRegisterModal = ref(false)

// 错误状态
const loginError = ref('')
const registerError = ref('')

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
const isDarkMode = ref(true)
const currentTheme = computed(() => isDarkMode.value ? 'theme-1' : 'theme-light')

// 暗黑模式切换函数
const toggleDarkMode = () => {
  isDarkMode.value = !isDarkMode.value
}

// 搜索相关状态
const searchQuery = ref('')
const searchResults = ref<HotItem[]>([])

// 搜索功能
const handleSearch = () => {
  if (!searchQuery.value.trim()) {
    searchResults.value = []
    return
  }
  
  const query = searchQuery.value.toLowerCase()
  const allItems: HotItem[] = []
  
  // 收集所有平台的数据
  const platforms = [
    { items: ngaItems.value, source: 'NGA' },
    { items: zhihuItems.value, source: '知乎' },
    { items: techItems.value, source: '值得买' },
    { items: weiboItems.value, source: '微博' },
    { items: bilibiliItems.value, source: 'B站' },
    { items: toutiaoItems.value, source: '今日头条' },
    { items: hupuItems.value, source: '虎扑' }
  ]
  
  platforms.forEach(platform => {
    platform.items.forEach(item => {
      if (item.title.toLowerCase().includes(query)) {
        allItems.push({
          ...item,
          source: platform.source
        })
      }
    })
  })
  
  searchResults.value = allItems.slice(0, 10) // 限制显示10个结果
}

// 清空搜索结果
const clearSearch = () => {
  searchResults.value = []
}

// 点击搜索结果项
const selectSearchResult = (url: string) => {
  openLink(url)
  clearSearch()
  searchQuery.value = ''
}

// 处理登录
const handleLogin = async () => {
  loginError.value = ''
  
  if (!loginForm.value.username || !loginForm.value.password) {
    loginError.value = 'Please fill in username and password'
    return
  }

  isLoading.value = true
  try {
    const result = await login(loginForm.value.username, loginForm.value.password)
    if (result.success) {
      addNotification('success', 'Login successful')
      showLoginModal.value = false
      loginForm.value = { username: '', password: '' }
      loginError.value = ''
    } else {
      loginError.value = result.error || 'Login failed'
    }
  } catch (error) {
    loginError.value = 'Login failed. Please try again.'
  } finally {
    isLoading.value = false
  }
}

// 处理注册
const handleRegister = async () => {
  registerError.value = ''
  
  if (!registerForm.value.username || !registerForm.value.email || !registerForm.value.password) {
    registerError.value = 'Please fill in all required fields'
    return
  }

  if (registerForm.value.password !== registerForm.value.confirmPassword) {
    registerError.value = 'Password confirmation does not match'
    return
  }

  isLoading.value = true
  try {
    const result = await register(registerForm.value)
    if (result.success) {
      addNotification('success', 'Registration successful, please login')
      showRegisterModal.value = false
      registerForm.value = { username: '', email: '', password: '', confirmPassword: '' }
      registerError.value = ''
    } else {
      registerError.value = result.error || 'Registration failed'
    }
  } catch (error) {
    registerError.value = 'Registration failed. Please try again.'
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

// 刷新状态管理
const refreshingPlatforms = ref<Record<string, boolean>>({})

// 定义API响应类型
interface ApiResponse {
  success: boolean
  data: {
    hot_lists: {
      platform_id: number
      name: string
      display_name: string
      api_endpoint: string
      items: {
        title: string
        url: string
        hot_value?: string | number
        rank_position?: number
      }[]
      total_count: number
      last_updated: string | null
    }[]
    total_platforms: number
    total_items: number
    last_updated: string
  }
}

// API调用函数
const fetchHotItems = async () => {
  try {
    const config = useRuntimeConfig()
    const response = await $fetch<ApiResponse>('/api/v1/hot', {
      baseURL: config.public.apiBase,
      query: {
        hours: 24,
        size: 30
      }
    })
    
    if (response.success && response.data && response.data.hot_lists) {
      // 按平台分组数据
      const groupedData: Record<string, HotItem[]> = {}
      response.data.hot_lists.forEach((hotList) => {
        const platform = hotList.display_name
        if (!groupedData[platform]) {
          groupedData[platform] = []
        }
        // 去重处理，避免重复标题
        const seenTitles = new Set<string>()
        hotList.items.forEach((item: any) => {
          if (!seenTitles.has(item.title)) {
            seenTitles.add(item.title)
            groupedData[platform].push({
              title: item.title,
              url: item.url,
              hot_value: item.score || item.hot_value || item.comment_count || 0,
              rank: item.rank_position
            })
          }
        })
      })
      
      // 更新各平台数据，确保即使没有数据也显示空数组
      ngaItems.value = groupedData['NGA玩家社区'] || []
      zhihuItems.value = groupedData['知乎'] || []
      weiboItems.value = groupedData['微博'] || []
      techItems.value = groupedData['什么值得买'] || []
      bilibiliItems.value = groupedData['B站'] || []
      toutiaoItems.value = groupedData['今日头条'] || []
      hupuItems.value = groupedData['虎扑'] || []
      ithomeItems.value = groupedData['IT之家'] || []
      zolItems.value = groupedData['中关村在线'] || []
      
      // 更新时间戳 - 使用正确的平台名称映射
      const now = new Date()
      const platformMapping: Record<string, string> = {
        'NGA玩家社区': 'nga',
        '知乎': 'zhihu',
        '微博': 'weibo',
        '什么值得买': 'smzdm',
        'B站': 'bilibili',
        '今日头条': 'toutiao',
        '虎扑': 'hupu',
        'IT之家': 'ithome'
      }
      Object.keys(groupedData).forEach(platform => {
        const mappedName = platformMapping[platform] || platform.toLowerCase()
        lastUpdateTimes.value[mappedName] = now
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
  if (!lastUpdate) return 'unknown'
  
  const now = new Date()
  const diff = Math.floor((now.getTime() - lastUpdate.getTime()) / (1000 * 60))
  
  if (diff < 1) return 'just now'
  if (diff < 60) return `${diff} min ago`
  if (diff < 1440) return `${Math.floor(diff / 60)} hr ago`
  return `${Math.floor(diff / 1440)} day ago`
}

// 格式化热度值
const formatHotValue = (value: string | number | undefined) => {
  if (!value) return ''
  
  // 如果是字符串且包含中文，直接返回
  if (typeof value === 'string' && /[\u4e00-\u9fa5]/.test(value)) {
    return value
  }
  
  const numValue = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(numValue) || numValue === 0) return ''
  
  if (numValue >= 10000) {
    return `${(numValue / 10000).toFixed(1)}万`
  }
  return numValue.toString()
}

// 打开链接函数
const openLink = (url: string) => {
  if (url && url !== '#') {
    window.open(url, '_blank')
  }
}

// 单个平台数据刷新
const refreshPlatformData = async (platformName: string) => {
  refreshingPlatforms.value[platformName] = true
  
  try {
    const config = useRuntimeConfig()
    const response = await $fetch<ApiResponse>(`/api/v1/hot/${platformName}`, {
      baseURL: config.public.apiBase,
      query: {
        hours: 24,
        size: 30
      }
    })
    
    if (response.success && response.data && response.data.hot_lists && response.data.hot_lists.length > 0) {
       const hotList = response.data.hot_lists[0]
       // 去重处理，避免重复标题
       const seenTitles = new Set<string>()
       const items: HotItem[] = hotList.items
         .filter((item: any) => {
           if (seenTitles.has(item.title)) {
             return false
           }
           seenTitles.add(item.title)
           return true
         })
         .map((item: any) => ({
           title: item.title,
           url: item.url,
           hot_value: item.score || item.hot_value || item.comment_count || 0,
           rank: item.rank_position
         }))
      
      // 根据平台名称更新对应的数据
      switch (platformName) {
        case 'nga':
          ngaItems.value = items
          break
        case 'zhihu':
          zhihuItems.value = items
          break
        case 'weibo':
          weiboItems.value = items
          break
        case 'smzdm':
          techItems.value = items
          break
        case 'bilibili':
          bilibiliItems.value = items
          break
        case 'toutiao':
          toutiaoItems.value = items
          break
        case 'hupu':
          hupuItems.value = items
          break
      }
      
      // 更新时间戳
      lastUpdateTimes.value[platformName] = new Date()
    }
  } catch (error) {
    console.error(`刷新${platformName}数据失败:`, error)
  } finally {
    refreshingPlatforms.value[platformName] = false
  }
}

// 页面加载时获取数据
onMounted(async () => {
  // 初始化认证状态
  await initAuth()
  
  // 加载用户配置
  loadUserConfig()
  
  // 获取热榜数据
  fetchHotItems()
  
  // 根据用户配置设置自动刷新
  if (userConfig.value.autoRefresh) {
    setInterval(fetchHotItems, userConfig.value.refreshInterval * 60 * 1000)
  }
  
  // 添加全局点击事件监听，点击外部时关闭搜索结果
  document.addEventListener('click', (event) => {
    const searchContainer = document.querySelector('.search-container')
    if (searchContainer && !searchContainer.contains(event.target as Node)) {
      clearSearch()
    }
  })
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

.theme-light {
  --bg-primary: #ffffff;
  --bg-secondary: #f8f9fa;
  --bg-card: #ffffff;
  --text-primary: #1a1a1a;
  --text-secondary: #6b7280;
  --text-muted: #9ca3af;
  --border-color: #e5e7eb;
  --icon-color: #6b7280;
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

.hot-content {
  height: 400px;
  overflow-y: auto;
  scrollbar-width: thin;
  scrollbar-color: #666 transparent;
}

.hot-content::-webkit-scrollbar {
  width: 4px;
}

.hot-content::-webkit-scrollbar-track {
  background: transparent;
}

.hot-content::-webkit-scrollbar-thumb {
  background: #666;
  border-radius: 2px;
}

.hot-content::-webkit-scrollbar-thumb:hover {
  background: #888;
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