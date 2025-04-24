<template>
  <div class="app-wrapper">
    <!-- 侧边栏 -->
    <div class="sidebar-container">
      <div class="logo-container">
        <router-link to="/">
          <h1 class="logo-title">问数智能体</h1>
        </router-link>
      </div>
      
      <!-- 菜单 -->
      <el-menu
        :default-active="activeMenu"
        class="sidebar-menu"
        background-color="#304156"
        text-color="#fff"
        active-text-color="#409EFF"
        router
      >
        <el-menu-item index="/dashboard">
          <el-icon><icon-house /></el-icon>
          <template #title>首页</template>
        </el-menu-item>
        
        <el-sub-menu index="/datasource">
          <template #title>
            <el-icon><icon-data-line /></el-icon>
            <span>数据源管理</span>
          </template>
          <el-menu-item index="/datasource/list">
            <el-icon><icon-list /></el-icon>
            <span>数据源列表</span>
          </el-menu-item>
          <el-menu-item index="/datasource/create">
            <el-icon><icon-plus /></el-icon>
            <span>新建数据源</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-sub-menu index="/model">
          <template #title>
            <el-icon><icon-monitor /></el-icon>
            <span>模型管理</span>
          </template>
          <el-menu-item index="/model/list">
            <el-icon><icon-list /></el-icon>
            <span>模型列表</span>
          </el-menu-item>
          <el-menu-item index="/model/create">
            <el-icon><icon-plus /></el-icon>
            <span>新建模型</span>
          </el-menu-item>
        </el-sub-menu>
        
        <el-menu-item index="/chat">
          <el-icon><icon-chat-dot-round /></el-icon>
          <template #title>会话界面</template>
        </el-menu-item>
      </el-menu>
    </div>
    
    <!-- 主要内容区域 -->
    <div class="main-container">
      <!-- 头部导航 -->
      <div class="navbar">
        <div class="left-area">
          <el-breadcrumb separator="/">
            <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
            <el-breadcrumb-item v-if="meta.title">{{ meta.title }}</el-breadcrumb-item>
          </el-breadcrumb>
        </div>
        <div class="right-menu">
          <el-dropdown trigger="click">
            <div class="avatar-wrapper">
              <el-avatar :size="32" icon="UserFilled" />
              <span class="user-name">{{ getUserName() }}</span>
              <el-icon><CaretBottom /></el-icon>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人信息</el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </div>
      
      <!-- 页面内容 -->
      <div class="app-main">
        <router-view />
      </div>
    </div>
  </div>
</template>

<script>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { logout } from '@/api/auth'

export default {
  name: 'LayoutMain',
  
  setup() {
    // 路由相关
    const route = useRoute()
    const router = useRouter()
    
    // 计算当前激活的菜单项
    const activeMenu = computed(() => '/' + route.path.split('/')[1])
    
    // 当前路由的元数据
    const meta = computed(() => route.meta || {})
    
    // 安全获取用户名
    const getUserName = () => {
      try {
        if (typeof localStorage !== 'undefined') {
          const userInfoStr = localStorage.getItem('userInfo')
          if (userInfoStr) {
            const userInfo = JSON.parse(userInfoStr)
            return userInfo.username || '用户'
          }
        }
        return '用户'
      } catch (error) {
        console.error('获取用户信息失败:', error)
        return '用户'
      }
    }
    
    // 处理登出
    const handleLogout = () => {
      // 调用登出API
      logout()
        .then(() => {
          // 清除本地存储的令牌和用户信息
          try {
            if (typeof localStorage !== 'undefined') {
              localStorage.removeItem('token')
              localStorage.removeItem('userInfo')
            }
          } catch (error) {
            console.error('清除存储失败:', error)
          }
          
          ElMessage.success('已成功登出')
          
          // 跳转到登录页
          router.push('/login')
        })
        .catch(error => {
          console.error('登出失败:', error)
          
          // 即使API失败，也清除本地存储并跳转
          try {
            if (typeof localStorage !== 'undefined') {
              localStorage.removeItem('token')
              localStorage.removeItem('userInfo')
            }
          } catch (error) {
            console.error('清除存储失败:', error)
          }
          router.push('/login')
        })
    }
    
    return {
      activeMenu,
      meta,
      handleLogout,
      getUserName
    }
  }
}
</script>

<style lang="scss" scoped>
.app-wrapper {
  display: flex;
  height: 100%;
  width: 100%;
}

.sidebar-container {
  width: 240px;
  height: 100%;
  background-color: #304156;
  color: white;
  transition: width 0.3s;
  overflow-y: auto;
  
  .logo-container {
    height: 60px;
    padding: 10px 0;
    text-align: center;
    
    .logo-title {
      color: white;
      margin: 0;
      font-size: 20px;
      line-height: 40px;
    }
    
    a {
      text-decoration: none;
    }
  }
  
  .sidebar-menu {
    border-right: none;
  }
}

.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  
  .navbar {
    height: 50px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #eee;
    padding: 0 15px;
    background-color: white;
    
    .left-area {
      display: flex;
      align-items: center;
    }
    
    .right-menu {
      display: flex;
      align-items: center;
      
      .avatar-wrapper {
        display: flex;
        align-items: center;
        cursor: pointer;
        
        .user-name {
          margin-left: 8px;
        }
      }
    }
  }
  
  .app-main {
    flex: 1;
    padding: 15px;
    overflow-y: auto;
    background-color: #f0f2f5;
  }
}
</style> 