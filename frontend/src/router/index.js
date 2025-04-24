import { createRouter, createWebHistory } from 'vue-router'

// 直接导入组件，不使用懒加载
import Layout from '@/views/layout/Layout.vue'
import Dashboard from '@/views/dashboard/Dashboard.vue'
import DataSourceList from '@/views/datasource/DataSourceList.vue'
import DataSourceForm from '@/views/datasource/DataSourceForm.vue'
import ModelList from '@/views/model/ModelList.vue'
import ModelForm from '@/views/model/ModelForm.vue'
import ChatView from '@/views/chat/ChatView.vue'
import Login from '@/views/auth/Login.vue'
import NotFound from '@/views/error/NotFound.vue'

// 路由配置
const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: Dashboard,
        meta: { title: '首页', icon: 'House', requiresAuth: true }
      }
    ]
  },
  {
    path: '/datasource',
    component: Layout,
    redirect: '/datasource/list',
    meta: { title: '数据源管理', icon: 'DataLine', requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'DataSourceList',
        component: DataSourceList,
        meta: { title: '数据源列表', icon: 'List', requiresAuth: true }
      },
      {
        path: 'create',
        name: 'DataSourceCreate',
        component: DataSourceForm,
        meta: { title: '新建数据源', icon: 'Plus', requiresAuth: true }
      },
      {
        path: 'edit/:id',
        name: 'DataSourceEdit',
        component: DataSourceForm,
        meta: { title: '编辑数据源', icon: 'Edit', requiresAuth: true },
        props: true
      }
    ]
  },
  {
    path: '/model',
    component: Layout,
    redirect: '/model/list',
    meta: { title: '模型管理', icon: 'Monitor', requiresAuth: true },
    children: [
      {
        path: 'list',
        name: 'ModelList',
        component: ModelList,
        meta: { title: '模型列表', icon: 'List', requiresAuth: true }
      },
      {
        path: 'create',
        name: 'ModelCreate',
        component: ModelForm,
        meta: { title: '新建模型', icon: 'Plus', requiresAuth: true }
      },
      {
        path: 'edit/:id',
        name: 'ModelEdit',
        component: ModelForm,
        meta: { title: '编辑模型', icon: 'Edit', requiresAuth: true },
        props: true
      }
    ]
  },
  {
    path: '/chat',
    component: Layout,
    children: [
      {
        path: '',
        name: 'Chat',
        component: ChatView,
        meta: { title: '会话界面', icon: 'ChatDotRound', requiresAuth: true }
      }
    ]
  },
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { title: '登录' },
    hidden: true
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    component: NotFound,
    hidden: true
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(process.env.BASE_URL),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  document.title = to.meta.title ? `${to.meta.title} - 问数智能体` : '问数智能体'
  
  // 获取本地存储的令牌
  const token = localStorage.getItem('token')
  
  // 判断该路由是否需要登录权限
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 路由需要验证，检查是否已登录
    if (!token) {
      // 未登录，重定向到登录页面
      next({
        path: '/login',
        // 保存我们所在的位置，以便以后再来
        query: { redirect: to.fullPath }
      })
    } else {
      // 已登录，正常跳转
      next()
    }
  } else {
    // 路由不需要验证
    
    // 如果已登录且要前往登录页，则重定向到首页
    if (token && to.path === '/login') {
      next({ path: '/' })
    } else {
      // 正常跳转
      next()
    }
  }
})

export default router 