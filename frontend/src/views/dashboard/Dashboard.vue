<template>
  <div class="dashboard-container">
    <el-row :gutter="20">
      <!-- 概览卡片区域 -->
      <el-col :span="24">
        <h2 class="section-title">系统概览</h2>
      </el-col>
      
      <!-- 数据源卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>数据源</span>
              <el-icon><icon-data-line /></el-icon>
            </div>
          </template>
          <div class="card-content">
            <div class="data-value">{{ datasourceCount }}</div>
            <div class="data-label">已连接数据源</div>
          </div>
          <el-button type="primary" plain size="small" @click="toDataSource">管理数据源</el-button>
        </el-card>
      </el-col>
      
      <!-- 模型卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>模型</span>
              <el-icon><icon-monitor /></el-icon>
            </div>
          </template>
          <div class="card-content">
            <div class="data-value">{{ modelCount }}</div>
            <div class="data-label">已配置模型</div>
          </div>
          <el-button type="primary" plain size="small" @click="toModel">管理模型</el-button>
        </el-card>
      </el-col>
      
      <!-- 会话卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>会话</span>
              <el-icon><icon-chat-dot-round /></el-icon>
            </div>
          </template>
          <div class="card-content">
            <div class="data-value">{{ chatCount }}</div>
            <div class="data-label">历史会话数</div>
          </div>
          <el-button type="success" plain size="small" @click="toChat">开始会话</el-button>
        </el-card>
      </el-col>
      
      <!-- 系统状态卡片 -->
      <el-col :xs="24" :sm="12" :md="8" :lg="6">
        <el-card class="dashboard-card">
          <template #header>
            <div class="card-header">
              <span>系统状态</span>
              <el-icon><icon-cpu /></el-icon>
            </div>
          </template>
          <div class="card-content">
            <div class="status-indicator">
              <div class="status-dot" :class="{ active: systemStatus === 'running' }"></div>
              <div class="status-text">{{ systemStatusText }}</div>
            </div>
          </div>
          <el-button type="info" plain size="small" @click="checkSystem">检查系统</el-button>
        </el-card>
      </el-col>
      
      <!-- 统计图表区域 -->
      <el-col :span="24" class="chart-section">
        <h2 class="section-title">统计数据</h2>
      </el-col>
      
      <!-- 会话统计图 -->
      <el-col :span="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近7天会话统计</span>
              <el-icon><icon-data-analysis /></el-icon>
            </div>
          </template>
          <div class="chart-container" ref="chatStatsChart"></div>
        </el-card>
      </el-col>
      
      <!-- 响应时间统计图 -->
      <el-col :span="24" :lg="12">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>平均响应时间</span>
              <el-icon><icon-timer /></el-icon>
            </div>
          </template>
          <div class="chart-container" ref="responseTimeChart"></div>
        </el-card>
      </el-col>
      
      <!-- 快速操作区域 -->
      <el-col :span="24" class="quick-actions-section">
        <h2 class="section-title">快速操作</h2>
      </el-col>
      
      <el-col :span="24">
        <el-card class="action-card">
          <div class="action-buttons">
            <el-button type="primary" @click="toChat">
              <el-icon><icon-chat-dot-round /></el-icon>
              <span>新建会话</span>
            </el-button>
            <el-button type="success" @click="toDataSource">
              <el-icon><icon-plus /></el-icon>
              <span>添加数据源</span>
            </el-button>
            <el-button type="warning" @click="toModel">
              <el-icon><icon-setting /></el-icon>
              <span>配置模型</span>
            </el-button>
            <el-button type="info" @click="showHelp">
              <el-icon><icon-question-filled /></el-icon>
              <span>使用帮助</span>
            </el-button>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import * as echarts from 'echarts'
import { ElMessage, ElMessageBox } from 'element-plus'

export default {
  name: 'Dashboard',
  
  setup() {
    // 路由实例
    const router = useRouter()
    
    // 统计数据
    const datasourceCount = ref(5)
    const modelCount = ref(3)
    const chatCount = ref(28)
    const systemStatus = ref('running')
    const systemStatusText = ref('系统运行正常')
    
    // 图表引用
    const chatStatsChart = ref(null)
    const responseTimeChart = ref(null)
    
    // 跳转方法
    const toDataSource = () => {
      router.push('/datasource/list')
    }
    
    const toModel = () => {
      router.push('/model/list')
    }
    
    const toChat = () => {
      router.push('/chat')
    }
    
    // 检查系统状态
    const checkSystem = () => {
      // 模拟API调用
      setTimeout(() => {
        systemStatus.value = 'running'
        systemStatusText.value = '系统运行正常'
        
        // 显示成功消息
        ElMessage({
          message: '系统状态检查完成',
          type: 'success'
        })
      }, 1000)
    }
    
    // 显示帮助信息
    const showHelp = () => {
      ElMessageBox.alert(
        '问数智能体是一个基于自然语言的智能数据库查询系统，支持多种数据源的连接、查询和可视化。您可以通过自然语言而不是SQL语句来查询各种数据源。',
        '使用帮助',
        {
          confirmButtonText: '知道了'
        }
      )
    }
    
    // 初始化图表
    const initCharts = () => {
      // 初始化会话统计图
      const chatStatsChartInstance = echarts.init(chatStatsChart.value)
      const chatStatsOption = {
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        },
        yAxis: {
          type: 'value'
        },
        series: [
          {
            name: '会话数',
            type: 'line',
            data: [5, 8, 3, 6, 10, 4, 2],
            smooth: true,
            areaStyle: {}
          }
        ],
        color: ['#409EFF']
      }
      chatStatsChartInstance.setOption(chatStatsOption)
      
      // 初始化响应时间图
      const responseTimeChartInstance = echarts.init(responseTimeChart.value)
      const responseTimeOption = {
        tooltip: {
          trigger: 'item'
        },
        series: [
          {
            name: '响应时间',
            type: 'gauge',
            detail: {
              formatter: '{value} ms',
              fontSize: 14
            },
            data: [{ value: 358, name: '平均响应时间' }],
            max: 1000
          }
        ]
      }
      responseTimeChartInstance.setOption(responseTimeOption)
      
      // 窗口大小调整时重绘图表
      window.addEventListener('resize', () => {
        chatStatsChartInstance.resize()
        responseTimeChartInstance.resize()
      })
    }
    
    // 组件挂载后初始化图表
    onMounted(() => {
      // 延迟一下以确保DOM已经渲染
      setTimeout(() => {
        initCharts()
      }, 100)
    })
    
    return {
      datasourceCount,
      modelCount,
      chatCount,
      systemStatus,
      systemStatusText,
      chatStatsChart,
      responseTimeChart,
      toDataSource,
      toModel,
      toChat,
      checkSystem,
      showHelp
    }
  }
}
</script>

<style lang="scss" scoped>
.dashboard-container {
  padding: 20px 0;
  
  .section-title {
    margin-top: 10px;
    margin-bottom: 20px;
    font-size: 18px;
    font-weight: bold;
    color: #606266;
    border-left: 4px solid #409EFF;
    padding-left: 10px;
  }
  
  .dashboard-card {
    margin-bottom: 20px;
    
    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      color: #606266;
    }
    
    .card-content {
      padding: 15px 0;
      text-align: center;
      
      .data-value {
        font-size: 32px;
        font-weight: bold;
        color: #409EFF;
        margin-bottom: 5px;
      }
      
      .data-label {
        font-size: 14px;
        color: #909399;
      }
      
      .status-indicator {
        display: flex;
        align-items: center;
        justify-content: center;
        
        .status-dot {
          width: 12px;
          height: 12px;
          border-radius: 50%;
          background-color: #F56C6C;
          margin-right: 8px;
          
          &.active {
            background-color: #67C23A;
          }
        }
        
        .status-text {
          font-size: 16px;
          color: #606266;
        }
      }
    }
    
    .el-button {
      display: block;
      margin: 0 auto;
    }
  }
  
  .chart-section, .quick-actions-section {
    margin-top: 20px;
  }
  
  .chart-card {
    margin-bottom: 20px;
    
    .chart-container {
      height: 300px;
    }
  }
  
  .action-card {
    margin-bottom: 20px;
    
    .action-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: 15px;
      justify-content: center;
      padding: 10px 0;
      
      .el-button {
        min-width: 120px;
      }
    }
  }
}

@media (max-width: 768px) {
  .action-buttons {
    flex-direction: column;
    
    .el-button {
      margin-bottom: 10px;
      width: 100%;
    }
  }
}
</style> 