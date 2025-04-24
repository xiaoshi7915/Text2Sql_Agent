<template>
  <div class="model-form-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <h3>{{ isEdit ? '编辑模型' : '新建模型' }}</h3>
        </div>
      </template>
      
      <el-form 
        ref="formRef" 
        :model="form" 
        :rules="rules" 
        label-width="120px" 
        class="model-form"
        v-loading="loading"
      >
        <!-- 基本信息部分 -->
        <h4 class="form-section-title">基本信息</h4>
        
        <el-form-item label="模型名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入模型名称" />
        </el-form-item>
        
        <el-form-item label="模型类型" prop="type">
          <el-select v-model="form.type" placeholder="请选择模型类型" style="width: 100%" @change="handleTypeChange">
            <el-option v-for="item in modelTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模型版本" prop="version">
          <el-input v-model="form.version" placeholder="请输入模型版本，例如: 1.0.0" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入模型描述信息" />
        </el-form-item>
        
        <!-- 连接信息部分 -->
        <h4 class="form-section-title">连接信息</h4>
        
        <el-form-item label="API端点" prop="endpoint">
          <el-input v-model="form.endpoint" placeholder="请输入API端点，例如: https://api.example.com/v1/models" />
        </el-form-item>
        
        <el-form-item label="API密钥" prop="apiKey">
          <el-input v-model="form.apiKey" type="password" placeholder="请输入API密钥" show-password />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="form.status"
            :active-value="'active'"
            :inactive-value="'offline'"
            active-text="活跃"
            inactive-text="离线"
          />
        </el-form-item>
        
        <!-- 模型参数部分 -->
        <h4 class="form-section-title">模型参数</h4>
        
        <template v-if="form.type === 'LLM'">
          <el-form-item label="温度" prop="parameters.temperature">
            <el-slider
              v-model="form.parameters.temperature"
              :min="0"
              :max="2"
              :step="0.1"
              show-input
              show-stops
              :marks="{0: '0', 1: '1', 2: '2'}"
            />
          </el-form-item>
          
          <el-form-item label="最大Token数" prop="parameters.maxTokens">
            <el-input-number v-model="form.parameters.maxTokens" :min="1" :max="32000" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="Top P" prop="parameters.topP">
            <el-slider
              v-model="form.parameters.topP"
              :min="0"
              :max="1"
              :step="0.05"
              show-input
              show-stops
              :marks="{0: '0', 0.5: '0.5', 1: '1'}"
            />
          </el-form-item>
        </template>
        
        <template v-else-if="form.type === 'Extractor'">
          <el-form-item label="批处理大小" prop="parameters.batchSize">
            <el-input-number v-model="form.parameters.batchSize" :min="1" :max="1000" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="超时(毫秒)" prop="parameters.timeout">
            <el-input-number v-model="form.parameters.timeout" :min="1000" :max="60000" :step="1000" style="width: 100%" />
          </el-form-item>
        </template>
        
        <template v-else-if="form.type === 'Optimizer'">
          <el-form-item label="优化级别" prop="parameters.optimizationLevel">
            <el-radio-group v-model="form.parameters.optimizationLevel">
              <el-radio value="low">低 (速度优先)</el-radio>
              <el-radio value="medium">中 (平衡)</el-radio>
              <el-radio value="high">高 (质量优先)</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="启用缓存">
            <el-switch v-model="form.parameters.enableCache" />
          </el-form-item>
        </template>
        
        <!-- 高级配置部分 -->
        <h4 class="form-section-title">
          <el-button link type="primary" @click="showAdvanced = !showAdvanced">
            <el-icon v-if="showAdvanced"><icon-arrow-down /></el-icon>
            <el-icon v-else><icon-arrow-right /></el-icon>
            高级配置
          </el-button>
        </h4>
        
        <div v-if="showAdvanced">
          <el-form-item label="并发请求数">
            <el-input-number v-model="form.concurrentRequests" :min="1" :max="50" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="重试策略">
            <el-select v-model="form.retryStrategy" placeholder="请选择重试策略" style="width: 100%">
              <el-option label="无重试" value="none" />
              <el-option label="固定延迟" value="fixed" />
              <el-option label="指数退避" value="exponential" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="最大重试次数" v-if="form.retryStrategy !== 'none'">
            <el-input-number v-model="form.maxRetries" :min="1" :max="10" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="请求超时(秒)">
            <el-input-number v-model="form.requestTimeout" :min="1" :max="300" style="width: 100%" />
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

export default {
  name: 'ModelForm',
  
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
    
    // 当前编辑的模型ID
    const currentId = computed(() => {
      return props.id || route.params.id
    })
    
    // 模型类型选项
    const modelTypeOptions = [
      { value: 'LLM', label: '大语言模型' },
      { value: 'Extractor', label: '数据抽取器' },
      { value: 'Optimizer', label: '查询优化器' }
    ]
    
    // 表单数据
    const form = reactive({
      name: '',
      type: 'LLM',
      version: '1.0.0',
      description: '',
      endpoint: '',
      apiKey: '',
      status: 'active',
      parameters: {
        // LLM参数
        temperature: 0.7,
        maxTokens: 2048,
        topP: 0.95,
        
        // Extractor参数
        batchSize: 100,
        timeout: 30000,
        
        // Optimizer参数
        optimizationLevel: 'medium',
        enableCache: true
      },
      concurrentRequests: 5,
      retryStrategy: 'exponential',
      maxRetries: 3,
      requestTimeout: 30
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入模型名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      type: [
        { required: true, message: '请选择模型类型', trigger: 'change' }
      ],
      version: [
        { required: true, message: '请输入模型版本', trigger: 'blur' }
      ],
      endpoint: [
        { required: true, message: '请输入API端点', trigger: 'blur' },
        { 
          validator: (rule, value, callback) => {
            // 如果值为空或者是有效的URL，则通过验证
            if (!value || /^(https?:\/\/|wss?:\/\/)/.test(value)) {
              callback();
            } else {
              callback(new Error('请输入有效的URL，必须以http://、https://、ws://或wss://开头'));
            }
          }, 
          trigger: 'blur' 
        }
      ],
      apiKey: [
        { required: !isEdit.value, message: '请输入API密钥', trigger: 'blur' }
      ]
    }
    
    // 处理模型类型变更
    const handleTypeChange = (type) => {
      // 不同模型类型使用不同的默认端点
      if (type === 'LLM') {
        if (!form.endpoint) {
          form.endpoint = 'https://api.example.com/v1/completions'
        }
      } else if (type === 'Extractor') {
        if (!form.endpoint) {
          form.endpoint = 'http://localhost:8000/extract'
        }
      } else if (type === 'Optimizer') {
        if (!form.endpoint) {
          form.endpoint = 'http://localhost:8001/optimize'
        }
      }
    }
    
    // 获取模型详情
    const fetchModel = async () => {
      if (!isEdit.value) return
      
      loading.value = true
      
      try {
        // 模拟API调用
        setTimeout(() => {
          // 实际项目中应该调用API获取数据
          // const response = await api.getModelById(currentId.value)
          // const data = response.data
          
          // 模拟数据
          const data = {
            id: currentId.value,
            name: 'DeepSeek-SQL-7B',
            type: 'LLM',
            version: '1.0.0',
            description: '基于DeepSeek-Coder的SQL生成模型，支持多种数据库方言',
            endpoint: 'https://api.deepseek.com/v1/sql',
            apiKey: '', // 出于安全考虑，通常不会返回密钥
            status: 'active',
            parameters: {
              temperature: 0.7,
              maxTokens: 2048,
              topP: 0.95
            },
            concurrentRequests: 5,
            retryStrategy: 'exponential',
            maxRetries: 3,
            requestTimeout: 30
          }
          
          // 更新表单数据
          Object.keys(form).forEach(key => {
            if (key === 'parameters') {
              // 合并参数对象
              Object.assign(form.parameters, data.parameters || {})
            } else if (data[key] !== undefined) {
              form[key] = data[key]
            }
          })
          
          loading.value = false
        }, 500)
      } catch (error) {
        console.error('获取模型详情失败', error)
        ElMessage.error('获取模型详情失败')
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
          // 模拟API调用
          setTimeout(() => {
            // 实际项目中应该调用API保存数据
            // if (isEdit.value) {
            //   await api.updateModel(currentId.value, form)
            // } else {
            //   await api.createModel(form)
            // }
            
            loading.value = false
            
            ElMessage({
              message: isEdit.value ? '模型更新成功' : '模型创建成功',
              type: 'success'
            })
            
            // 跳转到列表页
            router.push('/model/list')
          }, 1000)
        } catch (error) {
          console.error('保存模型失败', error)
          ElMessage.error('保存模型失败')
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
          // 模拟API调用
          setTimeout(() => {
            // 实际项目中应该调用API测试连接
            // await api.testModelConnection(form)
            
            loading.value = false
            
            // 随机模拟成功或失败
            const isSuccess = Math.random() > 0.3
            
            if (isSuccess) {
              ElMessage({
                message: '模型连接成功，响应时间: 235ms',
                type: 'success'
              })
            } else {
              ElMessage({
                message: '模型连接失败，请检查端点或API密钥',
                type: 'error'
              })
            }
          }, 1500)
        } catch (error) {
          console.error('测试连接失败', error)
          ElMessage.error('测试连接失败')
          loading.value = false
        }
      })
    }
    
    // 取消操作
    const handleCancel = () => {
      router.push('/model/list')
    }
    
    // 组件挂载时获取数据
    onMounted(() => {
      fetchModel()
    })
    
    return {
      formRef,
      loading,
      isEdit,
      form,
      rules,
      modelTypeOptions,
      showAdvanced,
      handleTypeChange,
      handleSubmit,
      handleTest,
      handleCancel
    }
  }
}
</script>

<style lang="scss" scoped>
.model-form-container {
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
  
  .model-form {
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
  .model-form-container {
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