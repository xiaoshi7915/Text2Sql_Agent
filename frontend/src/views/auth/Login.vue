<template>
  <div class="login-container">
    <div class="login-box">
      <div class="login-header">
        <h2>问数智能体</h2>
        <p>基于自然语言的智能数据库查询系统</p>
      </div>
      
      <el-form 
        ref="loginFormRef" 
        :model="loginForm" 
        :rules="loginRules" 
        class="login-form"
        @submit.prevent="handleLogin"
      >
        <el-form-item prop="username">
          <el-input 
            v-model="loginForm.username" 
            placeholder="用户名" 
            prefix-icon="User"
          />
        </el-form-item>
        
        <el-form-item prop="password">
          <el-input 
            v-model="loginForm.password" 
            type="password" 
            placeholder="密码" 
            prefix-icon="Lock"
            show-password
            @keyup.enter="handleLogin"
          />
        </el-form-item>
        
        <div class="login-options">
          <el-checkbox v-model="loginForm.remember">记住我</el-checkbox>
          <a href="#" class="forgot-password">忘记密码？</a>
        </div>
        
        <el-form-item>
          <el-button 
            type="primary" 
            :loading="loading" 
            class="login-button" 
            @click="handleLogin"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { login } from '@/api/auth'

export default {
  name: 'LoginView',
  
  setup() {
    const router = useRouter()
    const loginFormRef = ref(null)
    const loading = ref(false)
    
    // 登录表单数据
    const loginForm = reactive({
      username: '',
      password: '',
      remember: false
    })
    
    // 表单验证规则
    const loginRules = {
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: true, message: '请输入密码', trigger: 'blur' },
        { min: 6, message: '密码长度至少为6个字符', trigger: 'blur' }
      ]
    }
    
    // 登录处理函数
    const handleLogin = () => {
      loginFormRef.value.validate(valid => {
        if (!valid) return
        
        loading.value = true
        
        // 调用登录API
        login(loginForm)
          .then(res => {
            // 存储token和用户信息
            localStorage.setItem('token', res.token)
            localStorage.setItem('userInfo', JSON.stringify(res.user))
            
            ElMessage.success('登录成功')
            router.push('/')
          })
          .catch(error => {
            console.error('登录失败:', error)
            
            // 为了开发测试阶段，仍然保留模拟登录
            if (process.env.NODE_ENV === 'development') {
              // 模拟登录，只在开发环境使用
              localStorage.setItem('token', 'demo-token')
              localStorage.setItem('userInfo', JSON.stringify({ username: loginForm.username, role: 'admin' }))
              
              ElMessage.success('开发模式：模拟登录成功')
              router.push('/')
            }
          })
          .finally(() => {
            loading.value = false
          })
      })
    }
    
    return {
      loginFormRef,
      loginForm,
      loginRules,
      loading,
      handleLogin
    }
  }
}
</script>

<style lang="scss" scoped>
.login-container {
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
}

.login-box {
  width: 400px;
  padding: 40px;
  background-color: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.login-header {
  text-align: center;
  margin-bottom: 40px;
  
  h2 {
    font-size: 28px;
    color: #303133;
    margin-bottom: 10px;
  }
  
  p {
    font-size: 16px;
    color: #909399;
  }
}

.login-form {
  .el-input {
    margin-bottom: 20px;
  }
}

.login-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  
  .forgot-password {
    color: #409EFF;
    text-decoration: none;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

.login-button {
  width: 100%;
}
</style> 