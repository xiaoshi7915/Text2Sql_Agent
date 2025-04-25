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
        
        <el-form-item label="模型类型" prop="model_type">
          <el-select v-model="form.model_type" placeholder="请选择模型类型" style="width: 100%" @change="handleTypeChange">
            <el-option v-for="item in modelTypeOptions" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="模型版本" prop="api_version">
          <el-input v-model="form.api_version" placeholder="请输入模型版本，例如: 1.0.0" />
        </el-form-item>
        
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="4" placeholder="请输入模型描述信息" />
        </el-form-item>
        
        <!-- 连接信息部分 -->
        <h4 class="form-section-title">连接信息</h4>
        
        <el-form-item label="提供商" prop="provider">
          <el-input v-model="form.provider" placeholder="请输入模型提供商，例如: OpenAI, DeepSeek" />
        </el-form-item>
        
        <el-form-item label="API端点" prop="api_base">
          <el-input v-model="form.api_base" placeholder="请输入API端点，例如: https://api.example.com/v1/models" />
        </el-form-item>
        
        <el-form-item label="API密钥" prop="api_key">
          <el-input v-model="form.api_key" type="password" placeholder="请输入API密钥" show-password />
        </el-form-item>
        
        <el-form-item label="状态">
          <el-switch
            v-model="form.is_active"
            :active-value="true"
            :inactive-value="false"
            active-text="活跃"
            inactive-text="离线"
          />
        </el-form-item>
        
        <!-- 模型参数部分 -->
        <h4 class="form-section-title">模型参数</h4>
        
        <template v-if="form.model_type === 'LLM'">
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
          
          <el-form-item label="最大Token数" prop="parameters.max_tokens">
            <el-input-number v-model="form.parameters.max_tokens" :min="1" :max="32000" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="Top P" prop="parameters.top_p">
            <el-slider
              v-model="form.parameters.top_p"
              :min="0"
              :max="1"
              :step="0.05"
              show-input
              show-stops
              :marks="{0: '0', 0.5: '0.5', 1: '1'}"
            />
          </el-form-item>
        </template>
        
        <template v-else-if="form.model_type === 'Extractor'">
          <el-form-item label="批处理大小" prop="parameters.batch_size">
            <el-input-number v-model="form.parameters.batch_size" :min="1" :max="1000" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="超时(毫秒)" prop="parameters.timeout">
            <el-input-number v-model="form.parameters.timeout" :min="1000" :max="60000" :step="1000" style="width: 100%" />
          </el-form-item>
        </template>
        
        <template v-else-if="form.model_type === 'Optimizer'">
          <el-form-item label="优化级别" prop="parameters.optimization_level">
            <el-radio-group v-model="form.parameters.optimization_level">
              <el-radio value="low">低 (速度优先)</el-radio>
              <el-radio value="medium">中 (平衡)</el-radio>
              <el-radio value="high">高 (质量优先)</el-radio>
            </el-radio-group>
          </el-form-item>
          
          <el-form-item label="启用缓存">
            <el-switch v-model="form.parameters.enable_cache" />
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
            <el-input-number v-model="form.concurrent_requests" :min="1" :max="50" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="重试策略">
            <el-select v-model="form.retry_strategy" placeholder="请选择重试策略" style="width: 100%">
              <el-option label="无重试" value="none" />
              <el-option label="固定延迟" value="fixed" />
              <el-option label="指数退避" value="exponential" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="最大重试次数" v-if="form.retry_strategy !== 'none'">
            <el-input-number v-model="form.max_retries" :min="1" :max="10" style="width: 100%" />
          </el-form-item>
          
          <el-form-item label="请求超时(秒)">
            <el-input-number v-model="form.request_timeout" :min="1" :max="300" style="width: 100%" />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
// 导入API函数
import { getModel, createModel, updateModel, testModelConnection } from '@/api/model'

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
      model_type: 'LLM', // 更改为后端字段名
      api_version: '1.0.0', // 更改为后端字段名
      description: '',
      api_base: '', // 更改为后端字段名
      api_key: '', // 更改为后端字段名
      provider: '', // 添加提供商字段
      is_active: true, // 更改为后端字段名
      parameters: {
        // LLM参数
        temperature: 0.7,
        max_tokens: 2048, // 更改为后端字段名
        top_p: 0.95, // 更改为后端字段名
        
        // Extractor参数
        batch_size: 100, // 更改为后端字段名
        timeout: 30000,
        
        // Optimizer参数
        optimization_level: 'medium', // 更改为后端字段名
        enable_cache: true // 更改为后端字段名
      },
      is_default: false, // 添加默认模型字段
      concurrent_requests: 5, // 可选的额外字段
      retry_strategy: 'exponential', // 可选的额外字段
      max_retries: 3, // 可选的额外字段
      request_timeout: 30 // 可选的额外字段
    })
    
    // 表单验证规则
    const rules = {
      name: [
        { required: true, message: '请输入模型名称', trigger: 'blur' },
        { min: 2, max: 50, message: '长度在 2 到 50 个字符', trigger: 'blur' }
      ],
      model_type: [
        { required: true, message: '请选择模型类型', trigger: 'change' }
      ],
      api_version: [
        { required: true, message: '请输入模型版本', trigger: 'blur' }
      ],
      provider: [
        { required: true, message: '请输入提供商', trigger: 'blur' }
      ],
      api_base: [
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
      api_key: [
        { required: !isEdit.value, message: '请输入API密钥', trigger: 'blur' }
      ]
    }
    
    // 处理模型类型变更
    const handleTypeChange = (type) => {
      // 不同模型类型使用不同的默认端点
      if (type === 'LLM') {
        if (!form.api_base) {
          form.api_base = 'https://api.example.com/v1/completions'
        }
      } else if (type === 'Extractor') {
        if (!form.api_base) {
          form.api_base = 'http://localhost:8000/extract'
        }
      } else if (type === 'Optimizer') {
        if (!form.api_base) {
          form.api_base = 'http://localhost:8001/optimize'
        }
      }
    }
    
    // 获取模型详情
    const fetchModel = async () => {
      if (!isEdit.value) return
      
      loading.value = true
      
      try {
        // 实际API调用
        const response = await getModel(currentId.value)
        if (response.status === 'success') {
          const data = response.data
          
          // 更新表单数据
          Object.keys(form).forEach(key => {
            if (key === 'parameters') {
              // 合并参数对象
              Object.assign(form.parameters, data.parameters || {})
            } else if (data[key] !== undefined) {
              form[key] = data[key]
            }
          })
        } else {
          ElMessage.error(response.message || '获取模型详情失败')
        }
      } catch (error) {
        console.error('获取模型详情失败', error)
        ElMessage.error('获取模型详情失败')
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
          // 准备提交的数据 - 确保所有必要字段都包含在内
          const submitData = {
            name: form.name,
            provider: form.provider,
            model_type: form.model_type,
            api_base: form.api_base,
            api_key: form.api_key,
            api_version: form.api_version,
            // 不要从parameters中提取这些字段，它们应该是顶级字段
            temperature: form.parameters.temperature,
            max_tokens: form.parameters.max_tokens,
            is_default: form.is_default,
            is_active: form.is_active,
            // 将整个parameters对象作为参数传递
            parameters: {
              ...form.parameters
            }
          }
          
          console.log("提交的数据:", submitData);  // 添加日志便于调试
          
          let response
          if (isEdit.value) {
            response = await updateModel(currentId.value, submitData)
          } else {
            response = await createModel(submitData)
          }
          
          console.log("API响应:", response);  // 添加日志显示响应
          
          if (response && response.status === 'success') {
            ElMessage({
              message: isEdit.value ? '模型更新成功' : '模型创建成功',
              type: 'success'
            })
            
            // 跳转到列表页
            router.push('/model/list')
          } else {
            ElMessage.error(response?.message || '保存失败')
          }
        } catch (error) {
          console.error('保存模型失败', error)
          ElMessage.error('保存模型失败: ' + (error.message || '未知错误'))
        } finally {
          loading.value = false
        }
      })
    }
    
    // 测试连接
    const handleTest = async () => {
      if (!formRef.value) return;
      
      formRef.value.validate(async (valid) => {
        if (!valid) {
          return false;
        }
        
        loading.value = true;
        
        try {
          // 准备测试连接的数据
          const testData = {
            provider: form.provider,
            model_type: form.model_type,
            api_key: form.api_key,
            api_base: form.api_base
          };
          
          console.log('测试连接数据:', testData);
          
          const response = await testModelConnection(testData);
          console.log('测试连接响应:', response);
          
          // 根据响应状态显示消息
          if (response.status === 'success') {
            ElMessage({
              message: '模型连接测试成功',
              type: 'success'
            });
          } else {
            ElMessage({
              message: response.message || '模型连接测试失败',
              type: 'error'
            });
          }
        } finally {
          loading.value = false;
        }
      });
    };
    
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