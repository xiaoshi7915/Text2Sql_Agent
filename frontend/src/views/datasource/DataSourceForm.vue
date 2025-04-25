<template>
  <div class="datasource-form-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>{{ isEdit ? '编辑数据源' : '新建数据源' }}</h3>
        </div>
      </template>
      
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="120px" 
        class="datasource-form"
        v-loading="loading"
      >
        <!-- 基本信息部分 -->
        <h4 class="form-section-title">基本信息</h4>
        
        <el-form-item label="数据源名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入数据源名称" />
        </el-form-item>
        
        <el-form-item label="数据库类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择数据库类型" style="width: 100%">
            <el-option v-for="item in dbTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入数据源描述信息" />
        </el-form-item>
        
        <!-- 连接信息部分 -->
        <h4 class="form-section-title">连接信息</h4>
        
        <el-form-item label="主机地址" prop="host">
          <el-input v-model="form.host" placeholder="请输入主机地址" />
        </el-form-item>
        
        <el-form-item label="端口" prop="port">
          <el-input-number v-model="form.port" :min="1" :max="65535" controls-position="right" style="width: 100%" />
        </el-form-item>
        
        <el-form-item label="数据库名称" prop="database">
          <el-input v-model="form.database" placeholder="请输入数据库名称" />
        </el-form-item>
        
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        
        <!-- 高级配置部分 -->
        <h4 class="form-section-title">
          <el-button link type="primary" @click="showAdvanced = !showAdvanced">
            <el-icon v-if="showAdvanced"><icon-arrow-down /></el-icon>
            <el-icon v-else><icon-arrow-right /></el-icon>
            高级配置
          </el-button>
        </h4>
        
        <div v-if="showAdvanced">
          <el-form-item label="连接超时(秒)">
            <el-input-number v-model="form.timeout" :min="1" :max="300" controls-position="right" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="连接池大小">
            <el-input-number v-model="form.poolSize" :min="1" :max="100" controls-position="right" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="字符集">
            <el-select v-model="form.charset" placeholder="请选择字符集" style="width: 100%">
              <el-option label="UTF-8" value="utf8" />
              <el-option label="GBK" value="gbk" />
              <el-option label="UTF-16" value="utf16" />
              <el-option label="ASCII" value="ascii" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="元数据刷新">
            <el-select v-model="form.metadataRefresh" placeholder="请选择元数据刷新方式" style="width: 100%">
              <el-option label="手动" value="manual" />
              <el-option label="每天" value="daily" />
              <el-option label="每周" value="weekly" />
              <el-option label="每月" value="monthly" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="SSL连接">
            <el-switch v-model="form.useSSL" />
          </el-form-item>
        </div>
        
        <!-- 操作按钮 -->
        <div class="form-actions">
          <el-button @click="handleCancel">取消</el-button>
          <el-button type="primary" @click="handleSubmit">保存</el-button>
          <el-button type="success" @click="handleTest">测试连接</el-button>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useDatasourceStore } from '@/store/datasource'

export default {
  name: 'DataSourceForm',
  
  props: {
    id: {
      type: [String, Number],
      required: false
    }
  },
  
  setup(props) {
    // 路由相关
    const route = useRoute()
    const router = useRouter()
    
    // 使用数据源Store
    const datasourceStore = useDatasourceStore()
    
    // 表单引用
    const formRef = ref(null)
    
    // 加载状态
    const loading = ref(false)
    
    // 是否显示高级配置
    const showAdvanced = ref(false)
    
    // 是否为编辑模式
    const isEdit = computed(() => {
      return !!props.id || !!route.params.id
    })
    
    // 当前编辑的数据源ID
    const currentId = computed(() => {
      return props.id || route.params.id
    })
    
    // 数据库类型选项
    const dbTypeOptions = [
      { value: 'MySQL', label: 'MySQL' },
      { value: 'PostgreSQL', label: 'PostgreSQL' },
      { value: 'SQLServer', label: 'SQL Server' },
      { value: 'Oracle', label: 'Oracle' }
    ]
    
    // 表单数据
    const form = reactive({
      name: '',
      type: 'MySQL',
      description: '',
      host: '',
      port: 3306,
      database: '',
      username: '',
      password: '',
      timeout: 30,
      poolSize: 10,
      charset: 'utf8',
      metadataRefresh: 'manual',
      useSSL: false
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入数据源名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      type: [
        { required: true, message: '请选择数据库类型', trigger: 'change' }
      ],
      host: [
        { required: true, message: '请输入主机地址', trigger: 'blur' }
      ],
      port: [
        { required: true, message: '请输入端口号', trigger: 'blur' },
        { type: 'number', message: '端口必须为数字', trigger: 'blur' }
      ],
      database: [
        { required: true, message: '请输入数据库名称', trigger: 'blur' }
      ],
      username: [
        { required: true, message: '请输入用户名', trigger: 'blur' }
      ],
      password: [
        { required: !isEdit.value, message: '请输入密码', trigger: 'blur' }
      ]
    }
    
    // 根据数据库类型设置默认端口
    const setDefaultPort = (type) => {
      const portMap = {
        'MySQL': 3306,
        'PostgreSQL': 5432,
        'SQLServer': 1433,
        'Oracle': 1521
      }
      form.port = portMap[type] || 3306
    }
    
    // 监听数据库类型变化
    watch(() => form.type, (newType) => {
      setDefaultPort(newType)
    })
    
    // 获取数据源详情
    const fetchDataSource = async () => {
      if (!isEdit.value) return
      
      loading.value = true
      
      try {
        // 调用API获取数据源详情
        const data = await datasourceStore.fetchDatasource(currentId.value)
        
        if (data) {
          // 更新表单数据
          Object.keys(form).forEach(key => {
            // 适配后端字段名与前端字段名的差异
            if (key === 'type' && data['ds_type'] !== undefined) {
              form[key] = data['ds_type']
            } else if (data[key] !== undefined) {
              form[key] = data[key]
            }
          })
        }
      } catch (error) {
        console.error('获取数据源详情失败', error)
        ElMessage.error(`获取数据源详情失败: ${error.message}`)
      } finally {
        loading.value = false
      }
    }
    
    // 提交表单
    const handleSubmit = async () => {
      if (!formRef.value) return
      
      formRef.value.validate(async (valid) => {
        if (!valid) {
          return false
        }
        
        loading.value = true
        
        try {
          // 准备提交的数据
          const submitData = {
            name: form.name,
            ds_type: form.type, // 适配后端字段名
            description: form.description,
            host: form.host,
            port: form.port,
            database: form.database,
            username: form.username,
            password: form.password,
            options: {
              timeout: form.timeout,
              poolSize: form.poolSize,
              charset: form.charset,
              metadataRefresh: form.metadataRefresh,
              useSSL: form.useSSL
            }
          }
          
          // 调用API保存数据
          let result
          if (isEdit.value) {
            result = await datasourceStore.editDatasource(currentId.value, submitData)
          } else {
            result = await datasourceStore.addDatasource(submitData)
          }
          
          ElMessage({
            message: isEdit.value ? '数据源更新成功' : '数据源创建成功',
            type: 'success'
          })
          
          // 跳转到列表页
          router.push('/datasource/list')
        } catch (error) {
          console.error('保存数据源失败', error)
          ElMessage.error(`保存数据源失败: ${error.message}`)
        } finally {
          loading.value = false
        }
      })
    }
    
    // 测试连接
    const handleTest = async () => {
      if (!formRef.value) return
      
      formRef.value.validate(async (valid) => {
        if (!valid) {
          return false
        }
        
        loading.value = true
        
        try {
          // 准备提交的测试数据
          const testData = {
            ds_type: form.type,
            host: form.host,
            port: form.port,
            database: form.database,
            username: form.username,
            password: form.password
          }
          
          // 如果是编辑模式，添加ID
          if (isEdit.value) {
            testData.id = currentId.value
          }
          
          // 调用API测试连接
          const result = await datasourceStore.testConnection(testData)
          
          if (result.success) {
            // 显示表数量
            const tableCount = result.tables || 0
            
            ElMessage({
              message: `数据库连接成功，发现 ${tableCount} 个表`,
              type: 'success'
            })
            
            // 如果是编辑模式，刷新数据源信息
            if (isEdit.value) {
              await fetchDataSource()
            }
          } else {
            // 显示详细错误信息
            const errorMsg = result.error || '未知错误'
            const solution = result.details?.possible_solution
              ? `\n可能的解决方案: ${result.details.possible_solution}`
              : ''
            
            ElMessage({
              dangerouslyUseHTMLString: true,
              message: `<strong>连接失败</strong><br>${errorMsg}${solution ? `<br><br><em>${solution}</em>` : ''}`,
              type: 'error',
              duration: 5000,
              showClose: true
            })
            
            // 如果错误类型是认证插件错误，提示使用修复工具
            if (result.details?.error_type === 'auth_plugin_error') {
              ElMessage({
                dangerouslyUseHTMLString: true,
                message: `<strong>MySQL 8.0+ 认证问题</strong><br>请使用 <code>python backend/fix_mysql_connection.py</code> 修复认证插件或启用SSL连接`,
                type: 'warning',
                duration: 7000,
                showClose: true
              })
            }
            
            // 如果是编辑模式，刷新数据源信息以更新状态
            if (isEdit.value) {
              await fetchDataSource()
            }
          }
        } catch (error) {
          console.error('测试连接失败', error)
          
          // 尝试从错误响应中获取详细信息
          let errorMsg = '测试连接失败'
          let solution = ''
          
          if (error.response && error.response.data) {
            const responseData = error.response.data
            errorMsg = responseData.error || errorMsg
            solution = responseData.details?.possible_solution || ''
          } else {
            errorMsg = error.message || errorMsg
          }
          
          ElMessage({
            dangerouslyUseHTMLString: true,
            message: `<strong>连接失败</strong><br>${errorMsg}${solution ? `<br><br><em>${solution}</em>` : ''}`,
            type: 'error',
            duration: 5000,
            showClose: true
          })
          
          // 如果是编辑模式，刷新数据源信息以更新状态
          if (isEdit.value) {
            await fetchDataSource()
          }
        } finally {
          loading.value = false
        }
      })
    }
    
    // 取消操作
    const handleCancel = () => {
      router.push('/datasource/list')
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchDataSource()
    })
    
    return {
      formRef,
      loading,
      isEdit,
      form,
      rules,
      dbTypeOptions,
      showAdvanced,
      handleSubmit,
      handleTest,
      handleCancel
    }
  }
}
</script>

<style lang="scss" scoped>
.datasource-form-container {
  max-width: 800px;
  margin: 0 auto;
  
  .card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    
    h3 {
      margin: 0;
      color: #303133;
    }
  }
  
  .form-section-title {
    margin: 20px 0 15px;
    padding-bottom: 10px;
    border-bottom: 1px solid #ebeef5;
    color: #606266;
  }
  
  .datasource-form {
    .el-form-item {
      margin-bottom: 22px;
    }
  }
  
  .form-actions {
    display: flex;
    justify-content: center;
    gap: 15px;
    margin-top: 30px;
  }
}

@media (max-width: 768px) {
  .datasource-form-container {
    padding: 0 10px;
    
    .form-actions {
      flex-direction: column;
      
      .el-button {
        width: 100%;
        margin-bottom: 10px;
      }
    }
  }
}
</style> 