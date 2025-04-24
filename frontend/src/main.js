import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './assets/styles/main.scss'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import { registerIcons } from './icons'
import { setupGlobalResizeObserverErrorHandler } from './utils/resize-observer'
import { applyElementPlusPatches } from './utils/element-plus-patch'

// 初始化全局的ResizeObserver错误处理
setupGlobalResizeObserverErrorHandler();

// 应用 Element Plus 补丁
applyElementPlusPatches();

// 创建应用实例
const app = createApp(App)

// 注册所有Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 注册自定义图标组件
registerIcons(app)

// 创建并使用Pinia状态管理
const pinia = createPinia()
app.use(pinia)

// 使用路由
app.use(router)

// 使用Element Plus
app.use(ElementPlus, { size: 'default' })

// 挂载应用
app.mount('#app') 