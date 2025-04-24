<template>
  <div class="chat-container">
    <!-- 顶部导航栏 -->
    <div class="top-navbar">
      <div class="logo">
        <img src="@/assets/logo.png" alt="问数智能体" />
        <span>问数智能体</span>
      </div>
      <div class="nav-actions">
        <!-- 模型切换按钮 -->
        <el-dropdown @command="handleModelSwitch" trigger="click">
          <el-button type="primary">
            {{ getSelectedModelName() }}
            <el-icon class="el-icon--right"><icon-arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="model in availableModels" 
                :key="model.id" 
                :command="model.id"
                :class="{ 'is-active': selectedModel === model.id }"
              >
                {{ model.name }} ({{ model.type }})
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
        
        <!-- 数据源按钮 -->
        <el-dropdown @command="handleDataSourceAction" trigger="click">
          <el-button type="primary">
            数据源 ({{ selectedDataSources.length }})
            <el-icon class="el-icon--right"><icon-arrow-down /></el-icon>
          </el-button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item 
                v-for="source in availableDataSources" 
                :key="source.id" 
                :command="`select_${source.id}`"
              >
                <el-checkbox 
                  :value="selectedDataSources.includes(source.id)"
                  @click.stop="toggleDataSource(source.id)"
                >
                  {{ source.name }} ({{ source.type }})
                </el-checkbox>
              </el-dropdown-item>
              <el-dropdown-item divided command="manage">管理数据源</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <div class="main-content">
      <!-- 左侧会话列表 -->
      <div class="session-list-panel">
        <div class="panel-header">
          <h3>会话列表</h3>
          <el-button type="primary" size="small" @click="createNewSession">
            <el-icon><icon-plus /></el-icon>
            <span>新建会话</span>
          </el-button>
        </div>
        
        <div class="search-box">
          <el-input 
            v-model="searchKeyword" 
            placeholder="搜索会话" 
            clearable 
          >
            <template #prefix>
              <el-icon><icon-search /></el-icon>
            </template>
          </el-input>
        </div>
        
        <div class="session-list">
          <div 
            v-for="session in filteredSessions" 
            :key="session.id" 
            class="session-item"
            :class="{ active: session.id === currentSession.id }"
            @click="switchSession(session)"
          >
            <div class="session-icon">
              <el-icon><icon-chat-dot-round /></el-icon>
            </div>
            <div class="session-info">
              <div class="session-title">{{ session.title }}</div>
              <div class="session-meta">
                <span class="session-time">{{ formatDate(session.updatedAt) }}</span>
                <span class="session-count">{{ session.messageCount }}条</span>
              </div>
            </div>
            <div class="session-actions">
              <el-dropdown trigger="click" @command="handleSessionAction($event, session)">
                <el-icon><icon-more /></el-icon>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="rename">重命名</el-dropdown-item>
                    <el-dropdown-item command="export">导出</el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 右侧内容区域 -->
      <div class="content-panel">
        <!-- 对话区域 -->
        <div class="dialog-section">
          <div class="message-container" ref="messageContainer">
            <template v-if="currentSession.messages.length === 0">
              <div class="empty-state">
                <div class="empty-icon">
                  <el-icon><icon-chat-square /></el-icon>
                </div>
                <div class="empty-text">暂无消息，开始新的对话吧</div>
              </div>
            </template>
            
            <template v-else>
              <div 
                v-for="(message, index) in currentSession.messages" 
                :key="index"
                class="message-wrapper"
                :class="{'user-message': message.role === 'user', 'ai-message': message.role === 'assistant'}"
              >
                <div class="message-avatar">
                  <el-avatar>
                    <el-icon>
                      <icon-user v-if="message.role === 'user'" />
                      <icon-cpu v-else />
                    </el-icon>
                  </el-avatar>
                </div>
                <div class="message-content">
                  <div class="message-header">
                    <span class="message-sender">{{ message.role === 'user' ? '用户' : '智能体' }}</span>
                    <span class="message-time">{{ formatTime(message.timestamp) }}</span>
                  </div>
                  <div class="message-body" v-html="formatMessage(message.content)"></div>
                  <div class="message-actions" v-if="message.role === 'assistant'">
                    <el-button text type="primary" size="small" @click="copyMessage(message)">
                      <el-icon><icon-document-copy /></el-icon>
                      <span>复制</span>
                    </el-button>
                    <el-button text type="primary" size="small" @click="rateMessage(message, 'like')">
                      <el-icon><icon-thumb-up /></el-icon>
                      <span>有用</span>
                    </el-button>
                    <el-button text type="danger" size="small" @click="rateMessage(message, 'dislike')">
                      <el-icon><icon-thumb-down /></el-icon>
                      <span>无用</span>
                    </el-button>
                  </div>
                </div>
              </div>
              
              <div class="typing-indicator" v-if="isTyping">
                <span class="dot"></span>
                <span class="dot"></span>
                <span class="dot"></span>
              </div>
            </template>
          </div>
        </div>
        
        <!-- SQL显示区 -->
        <div class="sql-section" v-if="currentSQL">
          <div class="section-header">
            <h3>SQL 查询</h3>
            <div class="actions">
              <el-button size="small" @click="copySQLQuery">
                <el-icon><icon-document-copy /></el-icon>
                <span>复制</span>
              </el-button>
              <el-button size="small" @click="executeSQL" type="primary">
                <el-icon><icon-video-play /></el-icon>
                <span>执行</span>
              </el-button>
            </div>
          </div>
          <div class="sql-code">
            <pre><code>{{ currentSQL }}</code></pre>
          </div>
        </div>
        
        <!-- 查询结果区 -->
        <div class="result-section" v-if="queryResult.length > 0">
          <div class="section-header">
            <h3>查询结果</h3>
            <div class="actions">
              <el-button size="small" @click="exportResults">
                <el-icon><icon-download /></el-icon>
                <span>导出</span>
              </el-button>
            </div>
          </div>
          <div class="result-table">
            <el-table :data="queryResult" style="width: 100%" border stripe>
              <el-table-column 
                v-for="col in resultColumns" 
                :key="col" 
                :prop="col" 
                :label="col" 
              />
            </el-table>
          </div>
        </div>
        
        <!-- 可视化区域 -->
        <div class="visualization-section" v-if="hasVisualization">
          <div class="section-header">
            <h3>数据可视化</h3>
            <div class="actions">
              <el-dropdown @command="changeChartType">
                <el-button size="small">
                  图表类型
                  <el-icon class="el-icon--right"><icon-arrow-down /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="bar">柱状图</el-dropdown-item>
                    <el-dropdown-item command="line">折线图</el-dropdown-item>
                    <el-dropdown-item command="pie">饼图</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
              <el-button size="small" @click="exportChart">
                <el-icon><icon-picture /></el-icon>
                <span>导出</span>
              </el-button>
            </div>
          </div>
          <div class="chart-container" ref="chartContainer">
            <!-- 图表将在这里渲染 -->
          </div>
        </div>
        
        <!-- 输入区域 -->
        <div class="input-container">
          <div class="toolbar">
            <el-tooltip content="上传文件">
              <el-button circle @click="uploadFile">
                <el-icon><icon-upload /></el-icon>
              </el-button>
            </el-tooltip>
            <el-tooltip content="语音输入">
              <el-button circle @click="toggleVoiceInput">
                <el-icon><icon-microphone /></el-icon>
              </el-button>
            </el-tooltip>
          </div>
          
          <div class="input-area">
            <el-input
              v-model="messageInput"
              type="textarea"
              :rows="3"
              placeholder="输入您的问题..."
              resize="none"
              @keydown.enter.ctrl.prevent="sendMessage"
            />
            
            <el-button 
              type="primary" 
              :disabled="!messageInput.trim()" 
              @click="sendMessage"
            >
              发送
              <el-icon><icon-position /></el-icon>
            </el-button>
          </div>
          
          <div class="input-tips">
            按 Ctrl + Enter 发送消息
          </div>
        </div>
      </div>
    </div>
    
    <!-- 数据源预览抽屉 -->
    <el-drawer
      v-model="showDataSourcePanel"
      title="数据源预览"
      direction="rtl"
      size="60%"
    >
      <el-tabs type="border-card">
        <el-tab-pane label="元数据">
          <div class="metadata-view">
            <el-table :data="dataSourceMetadata" border>
              <el-table-column prop="tableName" label="表名" width="180" />
              <el-table-column prop="description" label="描述" width="180" />
              <el-table-column prop="rowCount" label="行数" />
              <el-table-column label="操作">
                <template #default="scope">
                  <el-button size="small" @click="viewTableDetails(scope.row)">
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-tab-pane>
        <el-tab-pane label="样例数据">
          <div class="sample-data-view">
            <el-select v-model="selectedTable" placeholder="选择表" style="width: 100%; margin-bottom: 15px;">
              <el-option
                v-for="table in availableTables"
                :key="table.name"
                :label="table.name"
                :value="table.name"
              />
            </el-select>
            
            <el-table v-if="selectedTable" :data="sampleData" border style="width: 100%">
              <el-table-column 
                v-for="col in sampleColumns" 
                :key="col" 
                :prop="col" 
                :label="col" 
              />
            </el-table>
          </div>
        </el-tab-pane>
      </el-tabs>
    </el-drawer>
    
    <!-- 表详情对话框 -->
    <el-dialog v-model="tableDetailsVisible" title="表结构详情" width="70%">
      <el-table :data="tableColumns" border style="width: 100%">
        <el-table-column prop="columnName" label="列名" width="180" />
        <el-table-column prop="dataType" label="数据类型" width="120" />
        <el-table-column prop="nullable" label="可为空">
          <template #default="scope">
            {{ scope.row.nullable ? '是' : '否' }}
          </template>
        </el-table-column>
        <el-table-column prop="isPrimaryKey" label="主键">
          <template #default="scope">
            {{ scope.row.isPrimaryKey ? '是' : '否' }}
          </template>
        </el-table-column>
        <el-table-column prop="description" label="描述" />
      </el-table>
    </el-dialog>
    
    <!-- 重命名会话对话框 -->
    <el-dialog v-model="renameDialogVisible" title="重命名会话" width="30%">
      <el-input v-model="newSessionTitle" placeholder="请输入新的会话名称"></el-input>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="renameDialogVisible = false">取消</el-button>
          <el-button type="primary" @click="confirmRename">确认</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, computed, onMounted, nextTick, watch, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as marked from 'marked'
import DOMPurify from 'dompurify'
import { v4 as uuidv4 } from 'uuid'
// 引入echarts (需要安装: npm install echarts)
import * as echarts from 'echarts'

export default {
  name: 'ChatView',
  
  components: {
  },
  
  setup() {
    // 路由实例
    const router = useRouter()
    
    // 会话列表搜索
    const searchKeyword = ref('')
    
    // 会话重命名相关
    const renameDialogVisible = ref(false)
    const newSessionTitle = ref('')
    const sessionToRename = ref(null)
    
    // 消息输入
    const messageInput = ref('')
    const isTyping = ref(false)
    const messageContainer = ref(null)
    
    // 图表相关
    const chartContainer = ref(null)
    const chartInstance = ref(null)
    const currentChartType = ref('bar')
    const hasVisualization = ref(false)
    
    // SQL相关
    const currentSQL = ref('')
    
    // 查询结果相关
    const queryResult = ref([])
    const resultColumns = ref([])
    
    // 数据源元数据和样例数据
    const showDataSourcePanel = ref(false)
    const dataSourceMetadata = ref([])
    const availableTables = ref([])
    const selectedTable = ref('')
    const sampleData = ref([])
    const sampleColumns = ref([])
    const tableDetailsVisible = ref(false)
    const tableColumns = ref([])
    
    // 数据源配置
    const availableDataSources = ref([
      { id: 1, name: '生产环境MySQL', type: 'MySQL' },
      { id: 2, name: '测试环境PostgreSQL', type: 'PostgreSQL' },
      { id: 3, name: '开发环境SQL Server', type: 'SQLServer' },
      { id: 4, name: '历史数据Oracle', type: 'Oracle' }
    ])
    const selectedDataSources = ref([1]) // 默认选择第一个数据源
    
    // 模型配置
    const availableModels = ref([
      { id: 1, name: 'GPT-4', type: '通用模型' },
      { id: 2, name: 'Claude 3', type: '通用模型' },
      { id: 3, name: 'LLaMA 3', type: '开源模型' },
      { id: 4, name: 'FinBERT', type: '金融专用模型' }
    ])
    const selectedModel = ref(1) // 默认选择第一个模型
    
    // 获取选中模型名称
    const getSelectedModelName = () => {
      const model = availableModels.value.find(m => m.id === selectedModel.value)
      return model ? model.name : '选择模型'
    }
    
    // 处理模型切换
    const handleModelSwitch = (modelId) => {
      selectedModel.value = modelId
      
      // 更新当前会话的模型
      currentSession.value.modelId = modelId
      
      // 更新会话列表
      const sessionIndex = sessions.value.findIndex(s => s.id === currentSession.value.id)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].modelId = modelId
      }
      
      ElMessage({
        message: `已切换到模型: ${getSelectedModelName()}`,
        type: 'success'
      })
    }
    
    // 切换数据源选择状态
    const toggleDataSource = (sourceId) => {
      const index = selectedDataSources.value.indexOf(sourceId)
      if (index === -1) {
        selectedDataSources.value.push(sourceId)
      } else {
        selectedDataSources.value.splice(index, 1)
      }
      
      // 更新当前会话的数据源
      currentSession.value.dataSourceIds = [...selectedDataSources.value]
      
      // 更新会话列表
      const sessionIndex = sessions.value.findIndex(s => s.id === currentSession.value.id)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].dataSourceIds = [...selectedDataSources.value]
      }
    }
    
    // 处理数据源操作
    const handleDataSourceAction = (command) => {
      if (command === 'manage') {
        showDataSourcePanel.value = true
        // 加载数据源元数据
        loadDataSourceMetadata()
      } else if (command.startsWith('select_')) {
        const sourceId = parseInt(command.split('_')[1])
        toggleDataSource(sourceId)
      }
    }
    
    // 加载数据源元数据
    const loadDataSourceMetadata = () => {
      // 实际项目中应该从API获取
      // 这里使用模拟数据
      dataSourceMetadata.value = [
        { tableName: 'users', description: '用户表', rowCount: 1500 },
        { tableName: 'orders', description: '订单表', rowCount: 45000 },
        { tableName: 'products', description: '产品表', rowCount: 3200 },
        { tableName: 'categories', description: '分类表', rowCount: 120 }
      ]
      
      availableTables.value = dataSourceMetadata.value.map(table => ({
        name: table.tableName,
        description: table.description
      }))
    }
    
    // 查看表详情
    const viewTableDetails = (table) => {
      // 实际项目中应该从API获取
      // 这里使用模拟数据
      if (table.tableName === 'users') {
        tableColumns.value = [
          { columnName: 'id', dataType: 'INT', nullable: false, isPrimaryKey: true, description: '用户ID' },
          { columnName: 'username', dataType: 'VARCHAR(50)', nullable: false, isPrimaryKey: false, description: '用户名' },
          { columnName: 'email', dataType: 'VARCHAR(100)', nullable: false, isPrimaryKey: false, description: '电子邮箱' },
          { columnName: 'password_hash', dataType: 'VARCHAR(128)', nullable: false, isPrimaryKey: false, description: '密码哈希' },
          { columnName: 'created_at', dataType: 'TIMESTAMP', nullable: false, isPrimaryKey: false, description: '创建时间' },
          { columnName: 'status', dataType: 'TINYINT', nullable: false, isPrimaryKey: false, description: '状态: 1-活跃, 0-禁用' }
        ]
      } else if (table.tableName === 'orders') {
        tableColumns.value = [
          { columnName: 'id', dataType: 'INT', nullable: false, isPrimaryKey: true, description: '订单ID' },
          { columnName: 'user_id', dataType: 'INT', nullable: false, isPrimaryKey: false, description: '用户ID' },
          { columnName: 'order_date', dataType: 'DATETIME', nullable: false, isPrimaryKey: false, description: '订单日期' },
          { columnName: 'total_amount', dataType: 'DECIMAL(10,2)', nullable: false, isPrimaryKey: false, description: '总金额' },
          { columnName: 'status', dataType: 'VARCHAR(20)', nullable: false, isPrimaryKey: false, description: '订单状态' }
        ]
      } else {
        tableColumns.value = [
          { columnName: 'id', dataType: 'INT', nullable: false, isPrimaryKey: true, description: '主键ID' },
          { columnName: 'name', dataType: 'VARCHAR(100)', nullable: false, isPrimaryKey: false, description: '名称' },
          { columnName: 'created_at', dataType: 'TIMESTAMP', nullable: false, isPrimaryKey: false, description: '创建时间' }
        ]
      }
      
      tableDetailsVisible.value = true
    }
    
    // 监听选中表变化，加载样例数据
    watch(selectedTable, (newValue) => {
      if (newValue) {
        loadSampleData(newValue)
      }
    })
    
    // 加载样例数据
    const loadSampleData = (tableName) => {
      // 实际项目中应该从API获取
      // 这里使用模拟数据
      if (tableName === 'users') {
        sampleData.value = [
          { id: 1, username: 'admin', email: 'admin@example.com', status: 1, created_at: '2023-01-15 08:30:00' },
          { id: 2, username: 'user1', email: 'user1@example.com', status: 1, created_at: '2023-02-20 10:15:00' },
          { id: 3, username: 'user2', email: 'user2@example.com', status: 0, created_at: '2023-03-05 14:45:00' }
        ]
        sampleColumns.value = ['id', 'username', 'email', 'status', 'created_at']
      } else if (tableName === 'orders') {
        sampleData.value = [
          { id: 1001, user_id: 1, order_date: '2023-10-15', total_amount: 1250.50, status: 'completed' },
          { id: 1002, user_id: 2, order_date: '2023-10-16', total_amount: 850.25, status: 'processing' },
          { id: 1003, user_id: 1, order_date: '2023-10-18', total_amount: 1450.00, status: 'completed' }
        ]
        sampleColumns.value = ['id', 'user_id', 'order_date', 'total_amount', 'status']
      } else if (tableName === 'products') {
        sampleData.value = [
          { id: 101, name: '数据分析服务', price: 599.99, category_id: 1 },
          { id: 102, name: '云存储套餐', price: 299.50, category_id: 2 },
          { id: 103, name: '安全防护服务', price: 499.00, category_id: 3 }
        ]
        sampleColumns.value = ['id', 'name', 'price', 'category_id']
      } else {
        sampleData.value = [
          { id: 1, name: '示例1', created_at: '2023-01-01' },
          { id: 2, name: '示例2', created_at: '2023-01-02' },
          { id: 3, name: '示例3', created_at: '2023-01-03' }
        ]
        sampleColumns.value = ['id', 'name', 'created_at']
      }
    }
    
    // 会话列表和当前会话
    const sessions = ref([
      {
        id: 1,
        title: '新建会话',
        createdAt: '2023-11-10T08:30:00Z',
        updatedAt: '2023-11-10T08:45:00Z',
        messageCount: 5,
        messages: [
          {
            id: 101,
            role: 'user',
            content: '你好，请查询一下我们的销售数据',
            timestamp: '2023-11-10T08:30:00Z'
          },
          {
            id: 102,
            role: 'assistant',
            content: '您好！我可以帮您查询销售数据。请问您需要查询哪个时间段、哪个地区或产品的销售数据呢？',
            timestamp: '2023-11-10T08:30:10Z'
          },
          {
            id: 103,
            role: 'user',
            content: '查询2023年10月的销售额',
            timestamp: '2023-11-10T08:31:00Z'
          },
          {
            id: 104,
            role: 'assistant',
            content: '我已查询到2023年10月的销售数据：\n\n总销售额：¥1,258,750\n同比增长：14.5%\n\n各产品线销售情况：\n- 数据服务：¥528,300 (42%)\n- 云存储：¥356,200 (28%)\n- 安全产品：¥245,600 (19%)\n- 其他服务：¥128,650 (11%)\n\n需要我为您提供更详细的分析吗？',
            timestamp: '2023-11-10T08:31:15Z'
          },
          {
            id: 105,
            role: 'user',
            content: '帮我分析一下销售趋势',
            timestamp: '2023-11-10T08:44:00Z'
          }
        ],
        dataSourceIds: [1],
        modelId: 1,
        sql: '',
        queryResults: []
      },
      {
        id: 2,
        title: '数据库查询示例',
        createdAt: '2023-11-09T10:15:00Z',
        updatedAt: '2023-11-09T10:30:00Z',
        messageCount: 3,
        messages: [],
        dataSourceIds: [1, 2],
        modelId: 1,
        sql: '',
        queryResults: []
      },
      {
        id: 3,
        title: '财务数据分析',
        createdAt: '2023-11-08T14:20:00Z',
        updatedAt: '2023-11-08T15:45:00Z',
        messageCount: 8,
        messages: [],
        dataSourceIds: [4],
        modelId: 4,
        sql: '',
        queryResults: []
      }
    ])
    
    // 当前会话
    const currentSession = ref({...sessions.value[0]})
    
    // 过滤会话列表
    const filteredSessions = computed(() => {
      if (!searchKeyword.value) return sessions.value
      
      const keyword = searchKeyword.value.toLowerCase()
      return sessions.value.filter(session => 
        session.title.toLowerCase().includes(keyword)
      )
    })
    
    // 创建新会话
    const createNewSession = () => {
      const newSession = {
        id: uuidv4(),
        title: `新建会话 ${sessions.value.length + 1}`,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        messageCount: 0,
        messages: [],
        dataSourceIds: [selectedDataSources.value[0]],
        modelId: selectedModel.value,
        sql: '',
        queryResults: []
      }
      
      sessions.value.unshift(newSession)
      currentSession.value = {...newSession}
      
      // 清空输入框和相关状态
      messageInput.value = ''
      currentSQL.value = '' 
      queryResult.value = []
      resultColumns.value = []
      hasVisualization.value = false
    }
    
    // 切换会话
    const switchSession = (session) => {
      // 如果点击的是当前会话，不做任何操作
      if (session.id === currentSession.value.id) return
      
      // 更新选中的数据源和模型
      selectedDataSources.value = session.dataSourceIds || [1]
      selectedModel.value = session.modelId || 1
      
      // 清空当前会话状态
      currentSQL.value = session.sql || ''
      queryResult.value = session.queryResults || []
      resultColumns.value = queryResult.value.length > 0 ? Object.keys(queryResult.value[0]) : []
      hasVisualization.value = Boolean(currentSQL.value && queryResult.value.length > 0 && 
                                     (currentSQL.value.toLowerCase().includes('count') || 
                                      currentSQL.value.toLowerCase().includes('group by')))
      
      // 切换会话
      currentSession.value = {...session}
      
      // 如果会话消息为空，加载消息
      if (!session.messages || session.messages.length === 0) {
        // 模拟加载消息
        loadSessionMessages(session.id)
      }
      
      // 滚动到最新消息
      nextTick(() => {
        scrollToBottom()
      })
      
      // 渲染图表（如果有）
      if (hasVisualization.value) {
        nextTick(() => {
          renderChart()
        })
      }
    }
    
    // 加载会话消息
    const loadSessionMessages = (sessionId) => {
      // 实际项目中应该从API获取消息
      // 这里使用模拟数据
      const sessionIndex = sessions.value.findIndex(s => s.id === sessionId)
      if (sessionIndex === -1) return
      
      // 模拟加载延迟
      setTimeout(() => {
        if (sessionId === 2) {
          // 数据库查询示例的模拟消息
          sessions.value[sessionIndex].messages = [
            {
              id: 201,
              role: 'user',
              content: '查询用户表的结构',
              timestamp: '2023-11-09T10:15:00Z'
            },
            {
              id: 202,
              role: 'assistant',
              content: '用户表(users)的结构如下：\n\n| 字段名 | 类型 | 说明 |\n| --- | --- | --- |\n| id | INT | 主键，自增 |\n| username | VARCHAR(50) | 用户名 |\n| email | VARCHAR(100) | 邮箱地址 |\n| password_hash | VARCHAR(128) | 密码哈希值 |\n| created_at | TIMESTAMP | 创建时间 |\n| status | TINYINT | 状态：1-活跃，0-禁用 |',
              timestamp: '2023-11-09T10:15:10Z'
            },
            {
              id: 203,
              role: 'user',
              content: '统计各状态的用户数量',
              timestamp: '2023-11-09T10:20:00Z'
            }
          ]
          
          // 添加SQL和查询结果
          sessions.value[sessionIndex].sql = 'SELECT status, COUNT(*) as count FROM users GROUP BY status;'
          sessions.value[sessionIndex].queryResults = [
            { status: '活跃', count: 1205 },
            { status: '禁用', count: 175 }
          ]
          
          currentSession.value = {...sessions.value[sessionIndex]}
          
          // 更新当前SQL和查询结果
          currentSQL.value = sessions.value[sessionIndex].sql
          queryResult.value = sessions.value[sessionIndex].queryResults
          resultColumns.value = ['status', 'count']
          
          // 开启可视化
          hasVisualization.value = true
          nextTick(() => {
            renderChart()
          })
          
        } else if (sessionId === 3) {
          // 财务数据分析的模拟消息
          sessions.value[sessionIndex].messages = [
            {
              id: 301,
              role: 'user',
              content: '分析2023年第三季度的财务状况',
              timestamp: '2023-11-08T14:20:00Z'
            },
            {
              id: 302,
              role: 'assistant',
              content: '2023年第三季度财务分析：\n\n**收入**：¥8,750,000\n**支出**：¥6,120,000\n**利润**：¥2,630,000\n**利润率**：30.1%\n\n与去年同期相比：\n- 收入增长：18.5%\n- 支出增长：12.3%\n- 利润增长：35.8%\n- 利润率提升：3.9个百分点\n\n主要收入来源：\n1. 产品销售：65%\n2. 服务订阅：25%\n3. 咨询服务：10%',
              timestamp: '2023-11-08T14:20:30Z'
            },
            {
              id: 303,
              role: 'user',
              content: '请生成一个可视化图表展示这些数据',
              timestamp: '2023-11-08T14:45:00Z'
            }
          ]
          
          // 添加SQL和查询结果
          sessions.value[sessionIndex].sql = 'SELECT category, revenue FROM financial_data WHERE quarter = 3 AND year = 2023;'
          sessions.value[sessionIndex].queryResults = [
            { category: '产品销售', revenue: 5687500 },
            { category: '服务订阅', revenue: 2187500 },
            { category: '咨询服务', revenue: 875000 }
          ]
          
          currentSession.value = {...sessions.value[sessionIndex]}
          
          // 更新当前SQL和查询结果
          currentSQL.value = sessions.value[sessionIndex].sql
          queryResult.value = sessions.value[sessionIndex].queryResults
          resultColumns.value = ['category', 'revenue']
          
          // 开启可视化
          hasVisualization.value = true
          nextTick(() => {
            renderChart()
          })
        }
      }, 500)
    }
    
    // 发送消息
    const sendMessage = async () => {
      if (!messageInput.value.trim()) return
      
      const userMessage = {
        id: uuidv4(),
        role: 'user',
        content: messageInput.value,
        timestamp: new Date().toISOString()
      }
      
      // 添加用户消息
      currentSession.value.messages.push(userMessage)
      
      // 更新会话信息
      const sessionIndex = sessions.value.findIndex(s => s.id === currentSession.value.id)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].messages = [...currentSession.value.messages]
        sessions.value[sessionIndex].messageCount = currentSession.value.messages.length
        sessions.value[sessionIndex].updatedAt = new Date().toISOString()
      }
      
      // 清空输入框
      messageInput.value = ''
      
      // 滚动到底部
      nextTick(() => {
        scrollToBottom()
      })
      
      // 显示输入中状态
      isTyping.value = true
      
      try {
        // 模拟AI回复延迟
        await new Promise(resolve => setTimeout(resolve, 1500))
        
        // 生成AI回复
        const aiResponse = await generateAIResponse(userMessage.content)
        
        // 处理可能包含的SQL
        let sql = ''
        let content = aiResponse
        
        // 检查是否包含SQL代码块
        const sqlMatch = aiResponse.match(/```sql\n([\s\S]*?)\n```/)
        if (sqlMatch && sqlMatch[1]) {
          sql = sqlMatch[1].trim()
          
          // 更新UI上的SQL显示
          currentSQL.value = sql
          
          // 如果实际应用中，这里可以自动执行SQL
          // executeSQL()
        }
        
        const aiMessage = {
          id: uuidv4(),
          role: 'assistant',
          content: content,
          timestamp: new Date().toISOString()
        }
        
        // 添加AI回复
        currentSession.value.messages.push(aiMessage)
        
        // 更新会话信息
        if (sessionIndex !== -1) {
          sessions.value[sessionIndex].messages = [...currentSession.value.messages]
          sessions.value[sessionIndex].messageCount = currentSession.value.messages.length
          sessions.value[sessionIndex].updatedAt = new Date().toISOString()
          
          // 保存SQL到会话
          if (sql) {
            sessions.value[sessionIndex].sql = sql
          }
        }
        
        // 隐藏输入中状态
        isTyping.value = false
        
        // 滚动到底部
        nextTick(() => {
          scrollToBottom()
        })
      } catch (error) {
        console.error('获取AI回复失败', error)
        isTyping.value = false
        
        // 显示错误消息
        ElMessage.error('获取回复失败，请重试')
      }
    }
    
    // 模拟AI回复生成
    const generateAIResponse = async (userInput) => {
      // 实际项目中应该调用API获取AI回复
      // 这里使用模拟数据
      
      const input = userInput.toLowerCase()
      
      if (input.includes('数据库') || input.includes('表') || input.includes('查询')) {
        // 添加SQL代码块
        const sql = input.includes('用户') || input.includes('账户') ? 
          'SELECT * FROM users WHERE status = 1;' :
          input.includes('订单') ? 
          'SELECT * FROM orders WHERE order_date >= "2023-10-01" AND order_date <= "2023-10-31";' :
          'SELECT * FROM products WHERE category_id = 1;'
        
        return '根据您的数据库查询，我找到了以下信息：\n\n```sql\n' + sql + '\n```\n\n查询结果显示有1,205个活跃用户，占总用户数的87.3%。非活跃用户有175个，占比12.7%。\n\n需要了解更详细的用户数据吗？'
      }
      
      if (input.includes('销售') || input.includes('营收') || input.includes('业绩')) {
        // 添加带有分组的SQL，适合可视化
        const sql = 'SELECT quarter, SUM(amount) as revenue FROM sales WHERE year = 2023 GROUP BY quarter;'
        
        return '2023年的销售数据分析如下：\n\n```sql\n' + sql + '\n```\n\n- 第一季度：¥3,456,000，同比增长15.2%\n- 第二季度：¥4,127,000，同比增长18.7%\n- 第三季度：¥4,890,000，同比增长21.3%\n- 第四季度：预计¥5,200,000，预计同比增长23.5%\n\n主要增长点来自于云服务和数据分析产品线。您需要查看更详细的产品线分析吗？'
      }
      
      if (input.includes('图表') || input.includes('可视化') || input.includes('展示')) {
        // 添加适合可视化的SQL
        const sql = 'SELECT category, COUNT(*) as count FROM products GROUP BY category;'
        
        return '以下是基于您请求的数据可视化SQL：\n\n```sql\n' + sql + '\n```\n\n您还需要其他类型的图表吗？例如饼图、折线图等。'
      }
      
      return '我理解您的问题是关于"' + userInput + '"。请问您需要查询哪些具体信息？您可以：\n\n1. 查询特定数据库表的结构和内容\n2. 分析业务数据和趋势\n3. 生成数据报表和可视化\n\n请告诉我您需要深入了解哪个方面的信息。'
    }
    
    // 复制消息内容
    const copyMessage = (message) => {
      navigator.clipboard.writeText(message.content)
        .then(() => {
          ElMessage({
            message: '已复制到剪贴板',
            type: 'success'
          })
        })
        .catch(() => {
          ElMessage.error('复制失败')
        })
    }
    
    // 评价消息
    const rateMessage = (message, rating) => {
      // 实际项目中应该调用API记录评价
      ElMessage({
        message: rating === 'like' ? '感谢您的肯定！' : '感谢您的反馈，我们会继续改进',
        type: rating === 'like' ? 'success' : 'warning'
      })
    }
    
    // 清空会话消息
    const clearMessages = () => {
      ElMessageBox.confirm(
        '确定要清空当前会话的所有消息吗？此操作不可撤销',
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(() => {
          // 清空当前会话消息
          currentSession.value.messages = []
          
          // 清空SQL和查询结果
          currentSession.value.sql = ''
          currentSession.value.queryResults = []
          currentSQL.value = ''
          queryResult.value = []
          resultColumns.value = []
          hasVisualization.value = false
          
          // 更新会话列表
          const sessionIndex = sessions.value.findIndex(s => s.id === currentSession.value.id)
          if (sessionIndex !== -1) {
            sessions.value[sessionIndex].messages = []
            sessions.value[sessionIndex].messageCount = 0
            sessions.value[sessionIndex].updatedAt = new Date().toISOString()
            sessions.value[sessionIndex].sql = ''
            sessions.value[sessionIndex].queryResults = []
          }
          
          ElMessage({
            type: 'success',
            message: '会话已清空'
          })
        })
        .catch(() => {
          // 取消操作
        })
    }
    
    // 会话操作处理
    const handleSessionAction = (command, session) => {
      switch (command) {
        case 'rename':
          sessionToRename.value = session
          newSessionTitle.value = session.title
          renameDialogVisible.value = true
          break
        case 'export':
          exportSession(session)
          break
        case 'delete':
          deleteSession(session)
          break
      }
    }
    
    // 确认重命名会话
    const confirmRename = () => {
      if (!newSessionTitle.value.trim()) {
        ElMessage.warning('会话名称不能为空')
        return
      }
      
      const sessionIndex = sessions.value.findIndex(s => s.id === sessionToRename.value.id)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].title = newSessionTitle.value
        
        // 如果重命名的是当前会话，也更新当前会话
        if (currentSession.value.id === sessionToRename.value.id) {
          currentSession.value.title = newSessionTitle.value
        }
        
        ElMessage({
          message: '重命名成功',
          type: 'success'
        })
      }
      
      renameDialogVisible.value = false
    }
    
    // 导出会话
    const exportSession = (session) => {
      // 构建导出数据
      const exportData = {
        title: session.title,
        createdAt: session.createdAt,
        updatedAt: session.updatedAt,
        messages: session.messages,
        sql: session.sql || '',
        queryResults: session.queryResults || []
      }
      
      // 转换为JSON字符串
      const dataStr = JSON.stringify(exportData, null, 2)
      
      // 创建下载链接
      const dataUri = 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr)
      const exportFileName = `chat-${session.title}-${new Date().toISOString().split('T')[0]}.json`
      
      // 创建下载链接并点击
      const linkElement = document.createElement('a')
      linkElement.setAttribute('href', dataUri)
      linkElement.setAttribute('download', exportFileName)
      linkElement.click()
      
      ElMessage({
        message: '导出成功',
        type: 'success'
      })
    }
    
    // 删除会话
    const deleteSession = (session) => {
      ElMessageBox.confirm(
        `确定要删除会话"${session.title}"吗？此操作不可撤销`,
        '警告',
        {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        }
      )
        .then(() => {
          // 从会话列表中删除
          sessions.value = sessions.value.filter(s => s.id !== session.id)
          
          // 如果删除的是当前会话，切换到第一个会话
          if (currentSession.value.id === session.id) {
            if (sessions.value.length > 0) {
              currentSession.value = {...sessions.value[0]}
              
              // 更新相关状态
              currentSQL.value = currentSession.value.sql || ''
              queryResult.value = currentSession.value.queryResults || []
              resultColumns.value = queryResult.value.length > 0 ? Object.keys(queryResult.value[0]) : []
              hasVisualization.value = Boolean(currentSQL.value && queryResult.value.length > 0 && 
                                            (currentSQL.value.toLowerCase().includes('count') || 
                                             currentSQL.value.toLowerCase().includes('group by')))
                                             
              if (hasVisualization.value) {
                nextTick(() => {
                  renderChart()
                })
              }
            } else {
              // 如果没有会话了，创建一个新会话
              createNewSession()
            }
          }
          
          ElMessage({
            type: 'success',
            message: '删除成功'
          })
        })
        .catch(() => {
          // 取消操作
        })
    }
    
    // 确认数据源选择
    const confirmDataSources = () => {
      // 更新当前会话的数据源
      currentSession.value.dataSourceIds = [...selectedDataSources.value]
      
      // 更新会话列表
      const sessionIndex = sessions.value.findIndex(s => s.id === currentSession.value.id)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].dataSourceIds = [...selectedDataSources.value]
      }
      
      showDataSourcePanel.value = false
      
      ElMessage({
        message: '数据源配置已更新',
        type: 'success'
      })
    }
    
    // 确认模型选择
    const confirmModel = () => {
      // 更新当前会话的模型
      currentSession.value.modelId = selectedModel.value
      
      // 更新会话列表
      const sessionIndex = sessions.value.findIndex(s => s.id === currentSession.value.id)
      if (sessionIndex !== -1) {
        sessions.value[sessionIndex].modelId = selectedModel.value
      }
      
      ElMessage({
        message: '模型配置已更新',
        type: 'success'
      })
    }
    
    // 上传文件
    const uploadFile = () => {
      // 实际项目中应该实现文件上传功能
      ElMessage({
        message: '文件上传功能正在开发中',
        type: 'info'
      })
    }
    
    // 语音输入
    const toggleVoiceInput = () => {
      // 实际项目中应该实现语音输入功能
      ElMessage({
        message: '语音输入功能正在开发中',
        type: 'info'
      })
    }
    
    // 格式化日期
    const formatDate = (dateString) => {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      const now = new Date()
      
      // 如果是今天
      if (date.toDateString() === now.toDateString()) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      
      // 如果是昨天
      const yesterday = new Date(now)
      yesterday.setDate(now.getDate() - 1)
      if (date.toDateString() === yesterday.toDateString()) {
        return '昨天 ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
      
      // 如果是今年
      if (date.getFullYear() === now.getFullYear()) {
        return date.toLocaleDateString([], { month: '2-digit', day: '2-digit' })
      }
      
      // 其他情况
      return date.toLocaleDateString()
    }
    
    // 格式化时间
    const formatTime = (dateString) => {
      if (!dateString) return ''
      
      const date = new Date(dateString)
      return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
    
    // 格式化消息内容，支持Markdown
    const formatMessage = (content) => {
      if (!content) return ''
      
      // 使用marked解析Markdown
      const html = marked.parse(content)
      
      // 使用DOMPurify清理HTML，防止XSS攻击
      return DOMPurify.sanitize(html)
    }
    
    // 滚动到底部
    const scrollToBottom = () => {
      if (messageContainer.value) {
        messageContainer.value.scrollTop = messageContainer.value.scrollHeight
      }
    }
    
    // 当消息列表变化时滚动到底部
    watch(
      () => currentSession.value.messages,
      () => {
        nextTick(() => {
          scrollToBottom()
        })
      },
      { deep: true }
    )
    
    // 监听窗口大小变化，重新渲染图表
    const handleResize = () => {
      if (hasVisualization.value && chartInstance.value) {
        chartInstance.value.resize()
      }
    }
    
    // 组件挂载时滚动到底部
    onMounted(() => {
      nextTick(() => {
        scrollToBottom()
      })
      
      // 添加窗口大小变化监听
      window.addEventListener('resize', handleResize)
    })
    
    // 组件卸载时清理
    onUnmounted(() => {
      // 移除窗口大小变化监听
      window.removeEventListener('resize', handleResize)
      
      // 销毁图表实例
      if (chartInstance.value) {
        chartInstance.value.dispose()
      }
    })
    
    // 复制SQL查询
    const copySQLQuery = () => {
      if (!currentSQL.value) return
      
      navigator.clipboard.writeText(currentSQL.value)
        .then(() => {
          ElMessage({
            message: 'SQL已复制到剪贴板',
            type: 'success'
          })
        })
        .catch(() => {
          ElMessage.error('复制失败')
        })
    }
    
    // 执行SQL查询
    const executeSQL = () => {
      if (!currentSQL.value) return
      
      // 实际项目中应该调用API执行SQL
      // 这里使用模拟数据
      ElMessage({
        message: '正在执行SQL查询...',
        type: 'info'
      })
      
      // 模拟延迟
      setTimeout(() => {
        // 根据SQL内容模拟不同的结果
        if (currentSQL.value.toLowerCase().includes('users')) {
          queryResult.value = [
            { id: 1, username: 'admin', email: 'admin@example.com', status: 1, created_at: '2023-01-15 08:30:00' },
            { id: 2, username: 'user1', email: 'user1@example.com', status: 1, created_at: '2023-02-20 10:15:00' },
            { id: 3, username: 'user2', email: 'user2@example.com', status: 0, created_at: '2023-03-05 14:45:00' },
            { id: 4, username: 'user3', email: 'user3@example.com', status: 1, created_at: '2023-04-10 09:20:00' },
            { id: 5, username: 'user4', email: 'user4@example.com', status: 1, created_at: '2023-05-22 11:10:00' }
          ]
          resultColumns.value = ['id', 'username', 'email', 'status', 'created_at']
        } else if (currentSQL.value.toLowerCase().includes('orders')) {
          queryResult.value = [
            { id: 1001, user_id: 1, order_date: '2023-10-15', total_amount: 1250.50, status: 'completed' },
            { id: 1002, user_id: 2, order_date: '2023-10-16', total_amount: 850.25, status: 'processing' },
            { id: 1003, user_id: 1, order_date: '2023-10-18', total_amount: 1450.00, status: 'completed' },
            { id: 1004, user_id: 3, order_date: '2023-10-20', total_amount: 950.75, status: 'completed' },
            { id: 1005, user_id: 2, order_date: '2023-10-22', total_amount: 1150.50, status: 'processing' }
          ]
          resultColumns.value = ['id', 'user_id', 'order_date', 'total_amount', 'status']
        } else if (currentSQL.value.toLowerCase().includes('count') || currentSQL.value.toLowerCase().includes('group by')) {
          queryResult.value = [
            { status: '活跃', count: 1205 },
            { status: '禁用', count: 175 }
          ]
          resultColumns.value = ['status', 'count']
          
          // 这种分组查询适合可视化
          hasVisualization.value = true
          nextTick(() => {
            renderChart()
          })
        } else {
          queryResult.value = [
            { result: 'SQL执行成功', affected_rows: 5 }
          ]
          resultColumns.value = ['result', 'affected_rows']
          hasVisualization.value = false
        }
        
        ElMessage({
          message: 'SQL执行成功',
          type: 'success'
        })
      }, 1000)
    }
    
    // 导出查询结果
    const exportResults = () => {
      if (queryResult.value.length === 0) return
      
      // 构建CSV内容
      const header = resultColumns.value.join(',')
      const rows = queryResult.value.map(row => {
        return resultColumns.value.map(col => {
          const value = row[col]
          // 处理包含逗号的字符串
          return typeof value === 'string' && value.includes(',') 
            ? `"${value}"` 
            : value
        }).join(',')
      })
      
      const csvContent = [header, ...rows].join('\n')
      
      // 创建下载链接
      const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
      const url = URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.setAttribute('href', url)
      link.setAttribute('download', `query-result-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      
      ElMessage({
        message: '查询结果已导出为CSV文件',
        type: 'success'
      })
    }
    
    // 改变图表类型
    const changeChartType = (type) => {
      currentChartType.value = type
      renderChart()
    }
    
    // 渲染图表
    const renderChart = () => {
      if (!chartContainer.value) return
      
      if (chartInstance.value) {
        chartInstance.value.dispose()
      }
      
      chartInstance.value = echarts.init(chartContainer.value)
      
      let option = {}
      
      if (currentChartType.value === 'bar') {
        option = {
          title: {
            text: '查询结果可视化'
          },
          tooltip: {},
          xAxis: {
            data: queryResult.value.map(item => item[resultColumns.value[0]])
          },
          yAxis: {},
          series: [{
            name: resultColumns.value[1],
            type: 'bar',
            coordinateSystem: 'cartesian2d',
            data: queryResult.value.map(item => item[resultColumns.value[1]])
          }]
        }
      } else if (currentChartType.value === 'line') {
        option = {
          title: {
            text: '查询结果可视化'
          },
          tooltip: {
            trigger: 'axis'
          },
          xAxis: {
            type: 'category',
            data: queryResult.value.map(item => item[resultColumns.value[0]])
          },
          yAxis: {
            type: 'value'
          },
          series: [{
            data: queryResult.value.map(item => item[resultColumns.value[1]]),
            type: 'line',
            coordinateSystem: 'cartesian2d'
          }]
        }
      } else if (currentChartType.value === 'pie') {
        option = {
          title: {
            text: '查询结果可视化',
            left: 'center'
          },
          tooltip: {
            trigger: 'item'
          },
          legend: {
            orient: 'vertical',
            left: 'left'
          },
          series: [
            {
              type: 'pie',
              radius: '50%',
              data: queryResult.value.map(item => ({
                name: item[resultColumns.value[0]],
                value: item[resultColumns.value[1]]
              })),
              emphasis: {
                itemStyle: {
                  shadowBlur: 10,
                  shadowOffsetX: 0,
                  shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
              }
            }
          ]
        }
      }
      
      chartInstance.value.setOption(option)
    }
    
    // 导出图表
    const exportChart = () => {
      if (!chartInstance.value) return
      
      const imageUrl = chartInstance.value.getDataURL({
        type: 'png',
        pixelRatio: 2,
        backgroundColor: '#fff'
      })
      
      const link = document.createElement('a')
      link.download = `chart-${currentChartType.value}-${new Date().toISOString().split('T')[0]}.png`
      link.href = imageUrl
      link.click()
      
      ElMessage({
        message: '图表已导出为图片文件',
        type: 'success'
      })
    }
    
    return {
      // 状态
      searchKeyword,
      messageInput,
      isTyping,
      renameDialogVisible,
      newSessionTitle,
      showDataSourcePanel,
      messageContainer,
      
      // 数据
      sessions,
      filteredSessions,
      currentSession,
      availableDataSources,
      selectedDataSources,
      availableModels,
      selectedModel,
      
      // 方法
      createNewSession,
      switchSession,
      sendMessage,
      copyMessage,
      rateMessage,
      clearMessages,
      handleSessionAction,
      confirmRename,
      confirmDataSources,
      confirmModel,
      uploadFile,
      toggleVoiceInput,
      
      // 工具函数
      formatDate,
      formatTime,
      formatMessage,
      scrollToBottom,
      
      // 图标组件
      
      // 新功能相关
      chartContainer,
      hasVisualization,
      currentSQL,
      queryResult,
      resultColumns,
      copySQLQuery,
      executeSQL,
      exportResults,
      changeChartType,
      exportChart,
      getSelectedModelName,
      handleModelSwitch,
      handleDataSourceAction,
      toggleDataSource,
      
      // 数据源管理相关
      dataSourceMetadata,
      availableTables,
      selectedTable,
      sampleData,
      sampleColumns,
      tableDetailsVisible,
      tableColumns,
      viewTableDetails
    }
  }
}
</script>

<style scoped>
.chat-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  overflow: hidden;
}

.top-navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 20px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 18px;
  font-weight: bold;
}

.logo img {
  height: 40px;
  margin-right: 10px;
}

.nav-actions {
  display: flex;
  gap: 10px;
}

.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
}

.session-list-panel {
  width: 280px;
  border-right: 1px solid #dcdfe6;
  display: flex;
  flex-direction: column;
  background-color: #f5f7fa;
}

.panel-header {
  padding: 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #dcdfe6;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
}

.search-box {
  padding: 10px 15px;
  border-bottom: 1px solid #dcdfe6;
}

.session-list {
  flex: 1;
  overflow-y: auto;
  padding: 10px 0;
}

.session-item {
  display: flex;
  padding: 12px 15px;
  cursor: pointer;
  transition: background-color 0.3s;
  border-radius: 4px;
  margin: 0 5px;
}

.session-item:hover {
  background-color: #e6f1fc;
}

.session-item.active {
  background-color: #ecf5ff;
}

.session-icon {
  margin-right: 12px;
  color: #409eff;
}

.session-info {
  flex: 1;
  min-width: 0;
}

.session-title {
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 5px;
}

.session-meta {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #909399;
}

.session-actions {
  visibility: hidden;
  color: #909399;
}

.session-item:hover .session-actions {
  visibility: visible;
}

.content-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.dialog-section {
  flex: 1;
  overflow: hidden;
  padding: 20px;
  position: relative;
}

.sql-section, .result-section, .visualization-section {
  border-top: 1px solid #dcdfe6;
  padding: 15px;
  background-color: #fff;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
}

.sql-code {
  background-color: #f8f8f8;
  border-radius: 4px;
  padding: 10px;
  overflow-x: auto;
  font-family: monospace;
  white-space: pre-wrap;
}

.chart-container {
  height: 300px;
  width: 100%;
}

.message-container {
  height: 100%;
  overflow-y: auto;
  padding: 10px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #909399;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.message-wrapper {
  display: flex;
  margin-bottom: 20px;
}

.user-message {
  flex-direction: row-reverse;
}

.message-avatar {
  margin: 0 10px;
}

.message-content {
  max-width: 70%;
  border-radius: 10px;
  padding: 12px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.user-message .message-content {
  background-color: #ecf5ff;
}

.ai-message .message-content {
  background-color: #f5f7fa;
}

.message-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 12px;
}

.message-sender {
  font-weight: bold;
}

.message-time {
  color: #909399;
}

.message-body {
  margin-bottom: 8px;
  line-height: 1.5;
}

.message-body pre {
  background-color: #f8f8f8;
  border-radius: 4px;
  padding: 10px;
  overflow-x: auto;
  font-family: monospace;
}

.message-actions {
  display: flex;
  justify-content: flex-end;
}

.input-container {
  border-top: 1px solid #dcdfe6;
  padding: 15px;
  background-color: #fff;
}

.toolbar {
  display: flex;
  margin-bottom: 10px;
  gap: 10px;
}

.input-area {
  display: flex;
  gap: 10px;
}

.input-area .el-textarea {
  flex: 1;
}

.input-tips {
  text-align: right;
  font-size: 12px;
  color: #909399;
  margin-top: 5px;
}

.typing-indicator {
  display: flex;
  padding: 5px 10px;
  margin-left: 50px;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background-color: #909399;
  margin: 0 2px;
  animation: wave 1.3s linear infinite;
}

.dot:nth-child(2) {
  animation-delay: -1.1s;
}

.dot:nth-child(3) {
  animation-delay: -0.9s;
}

@keyframes wave {
  0%, 60%, 100% {
    transform: initial;
  }
  30% {
    transform: translateY(-10px);
  }
}

.datasource-item, .model-item {
  padding: 10px;
  border-bottom: 1px solid #ebeef5;
}

.datasource-info, .model-info {
  display: flex;
  flex-direction: column;
}

.datasource-name, .model-name {
  font-weight: 500;
  margin-bottom: 5px;
}

.datasource-type, .model-type {
  font-size: 12px;
  color: #909399;
}

.drawer-footer {
  display: flex;
  justify-content: flex-end;
  padding: 15px 0;
}

.is-active {
  color: #409eff;
  font-weight: bold;
}

/* 响应式调整 */
@media screen and (max-width: 768px) {
  .main-content {
    flex-direction: column;
  }
  
  .session-list-panel {
    width: 100%;
    height: 200px;
    border-right: none;
    border-bottom: 1px solid #dcdfe6;
  }
  
  .content-panel {
    flex: 1;
  }
  
  .message-content {
    max-width: 85%;
  }
}
</style> 