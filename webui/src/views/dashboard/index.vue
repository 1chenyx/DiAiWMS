<template>
  <div class="dashboard">
    <div class="dashboard-header">
      <div class="header-content">
        <h1 class="page-title">仪表盘</h1>
        <p class="page-subtitle">欢迎回来，这是您的数据概览</p>
      </div>
      <div class="header-actions">
        <el-date-picker
          v-model="dateRange"
          type="daterange"
          range-separator="至"
          start-placeholder="开始日期"
          end-placeholder="结束日期"
          size="large"
        />
      </div>
    </div>
    
    <div class="stats-grid">
      <div 
        v-for="(stat, index) in statsData" 
        :key="index"
        class="stat-card"
        :class="`stat-card-${index + 1}`"
      >
        <div class="stat-header">
          <div class="stat-icon" :style="{ backgroundColor: stat.iconBg }">
            <component :is="stat.icon" />
          </div>
          <div class="stat-trend" :class="stat.trend > 0 ? 'trend-up' : 'trend-down'">
            <el-icon>
              <ArrowUp v-if="stat.trend > 0" />
              <ArrowDown v-else />
            </el-icon>
            <span>{{ Math.abs(stat.trend) }}%</span>
          </div>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ formatNumber(stat.value) }}</div>
          <div class="stat-label">{{ stat.label }}</div>
        </div>
        <div class="stat-footer">
          <span class="stat-compare">较上周</span>
          <span :class="stat.trend > 0 ? 'text-success' : 'text-danger'">
            {{ stat.trend > 0 ? '+' : '' }}{{ stat.trend }}%
          </span>
        </div>
      </div>
    </div>
    
    <div class="charts-grid">
      <el-card class="chart-card chart-card-large" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <h3>库存趋势</h3>
              <p>近7天库存变化情况</p>
            </div>
            <div class="card-actions">
              <el-radio-group v-model="chartType" size="small">
                <el-radio-button label="week">周</el-radio-button>
                <el-radio-button label="month">月</el-radio-button>
                <el-radio-button label="year">年</el-radio-button>
              </el-radio-group>
            </div>
          </div>
        </template>
        <div class="chart-container">
          <div class="chart-placeholder">
            <svg viewBox="0 0 400 200" class="trend-chart">
              <defs>
                <linearGradient id="gradient" x1="0%" y1="0%" x2="0%" y2="100%">
                  <stop offset="0%" style="stop-color:#667eea;stop-opacity:0.3" />
                  <stop offset="100%" style="stop-color:#667eea;stop-opacity:0" />
                </linearGradient>
              </defs>
              <path
                d="M 0 150 Q 50 120 100 130 T 200 100 T 300 120 T 400 80"
                fill="none"
                stroke="#667eea"
                stroke-width="3"
              />
              <path
                d="M 0 150 Q 50 120 100 130 T 200 100 T 300 120 T 400 80 V 200 H 0 Z"
                fill="url(#gradient)"
              />
              <circle cx="100" cy="130" r="5" fill="#667eea" />
              <circle cx="200" cy="100" r="5" fill="#667eea" />
              <circle cx="300" cy="120" r="5" fill="#667eea" />
              <circle cx="400" cy="80" r="5" fill="#667eea" />
            </svg>
          </div>
        </div>
      </el-card>
      
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <h3>入库出库对比</h3>
              <p>本月数据对比</p>
            </div>
          </div>
        </template>
        <div class="chart-container">
          <div class="comparison-bars">
            <div class="bar-item">
              <div class="bar-label">入库</div>
              <div class="bar-wrapper">
                <div class="bar bar-inbound" style="width: 75%"></div>
              </div>
              <div class="bar-value">1,234</div>
            </div>
            <div class="bar-item">
              <div class="bar-label">出库</div>
              <div class="bar-wrapper">
                <div class="bar bar-outbound" style="width: 60%"></div>
              </div>
              <div class="bar-value">987</div>
            </div>
            <div class="bar-item">
              <div class="bar-label">调拨</div>
              <div class="bar-wrapper">
                <div class="bar bar-transfer" style="width: 45%"></div>
              </div>
              <div class="bar-value">456</div>
            </div>
            <div class="bar-item">
              <div class="bar-label">盘点</div>
              <div class="bar-wrapper">
                <div class="bar bar-check" style="width: 30%"></div>
              </div>
              <div class="bar-value">234</div>
            </div>
          </div>
        </div>
      </el-card>
      
      <el-card class="chart-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <h3>仓库使用率</h3>
              <p>各仓库容量占比</p>
            </div>
          </div>
        </template>
        <div class="chart-container">
          <div class="warehouse-stats">
            <div class="warehouse-item">
              <div class="warehouse-info">
                <span class="warehouse-name">主仓库</span>
                <span class="warehouse-percent">85%</span>
              </div>
              <el-progress 
                :percentage="85" 
                :show-text="false"
                :stroke-width="8"
                color="#667eea"
              />
            </div>
            <div class="warehouse-item">
              <div class="warehouse-info">
                <span class="warehouse-name">分仓库A</span>
                <span class="warehouse-percent">62%</span>
              </div>
              <el-progress 
                :percentage="62" 
                :show-text="false"
                :stroke-width="8"
                color="#10B981"
              />
            </div>
            <div class="warehouse-item">
              <div class="warehouse-info">
                <span class="warehouse-name">分仓库B</span>
                <span class="warehouse-percent">45%</span>
              </div>
              <el-progress 
                :percentage="45" 
                :show-text="false"
                :stroke-width="8"
                color="#F59E0B"
              />
            </div>
            <div class="warehouse-item">
              <div class="warehouse-info">
                <span class="warehouse-name">临时仓库</span>
                <span class="warehouse-percent">28%</span>
              </div>
              <el-progress 
                :percentage="28" 
                :show-text="false"
                :stroke-width="8"
                color="#EF4444"
              />
            </div>
          </div>
        </div>
      </el-card>
    </div>
    
    <div class="bottom-section">
      <el-card class="activity-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <h3>最近操作</h3>
              <p>实时操作记录</p>
            </div>
            <el-button text type="primary">
              查看全部
              <el-icon class="ml-1"><ArrowRight /></el-icon>
            </el-button>
          </div>
        </template>
        <div class="activity-list">
          <div 
            v-for="(activity, index) in recentActivities" 
            :key="index"
            class="activity-item"
          >
            <div class="activity-icon" :class="`activity-icon-${activity.type}`">
              <component :is="getActivityIcon(activity.type)" />
            </div>
            <div class="activity-content">
              <div class="activity-title">{{ activity.action }}</div>
              <div class="activity-meta">
                <span class="activity-user">{{ activity.user }}</span>
                <span class="activity-time">{{ activity.time }}</span>
              </div>
            </div>
            <el-tag 
              :type="activity.status === '成功' ? 'success' : 'danger'" 
              size="small"
            >
              {{ activity.status }}
            </el-tag>
          </div>
        </div>
      </el-card>
      
      <el-card class="quick-actions-card" shadow="hover">
        <template #header>
          <div class="card-header">
            <div class="card-title">
              <h3>快捷操作</h3>
              <p>常用功能入口</p>
            </div>
          </div>
        </template>
        <div class="quick-actions">
          <div class="action-item" @click="handleQuickAction('inbound')">
            <div class="action-icon action-icon-inbound">
              <el-icon><Upload /></el-icon>
            </div>
            <span class="action-label">入库操作</span>
          </div>
          <div class="action-item" @click="handleQuickAction('outbound')">
            <div class="action-icon action-icon-outbound">
              <el-icon><Download /></el-icon>
            </div>
            <span class="action-label">出库操作</span>
          </div>
          <div class="action-item" @click="handleQuickAction('stock')">
            <div class="action-icon action-icon-stock">
              <el-icon><Search /></el-icon>
            </div>
            <span class="action-label">库存查询</span>
          </div>
          <div class="action-item" @click="handleQuickAction('report')">
            <div class="action-icon action-icon-report">
              <el-icon><Document /></el-icon>
            </div>
            <span class="action-label">报表中心</span>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { 
  Box, ArrowUp, ArrowDown, Timer, Upload, Download, 
  Search, Document, ArrowRight, Check, Close, Refresh
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const router = useRouter()
const dateRange = ref([])
const chartType = ref('week')

const statsData = ref([
  {
    label: '库存总量',
    value: 12345,
    trend: 12.5,
    icon: Box,
    iconBg: 'rgba(102, 126, 234, 0.1)'
  },
  {
    label: '今日入库',
    value: 456,
    trend: 8.3,
    icon: ArrowUp,
    iconBg: 'rgba(16, 185, 129, 0.1)'
  },
  {
    label: '今日出库',
    value: 789,
    trend: -3.2,
    icon: ArrowDown,
    iconBg: 'rgba(245, 158, 11, 0.1)'
  },
  {
    label: '待处理任务',
    value: 23,
    trend: -15.6,
    icon: Timer,
    iconBg: 'rgba(239, 68, 68, 0.1)'
  }
])

const recentActivities = ref([
  {
    type: 'inbound',
    action: '创建入库单 ASN-20260228-001',
    user: '管理员',
    time: '5分钟前',
    status: '成功'
  },
  {
    type: 'outbound',
    action: '完成出库操作',
    user: '张三',
    time: '15分钟前',
    status: '成功'
  },
  {
    type: 'stock',
    action: '调整库存 SKU001',
    user: '李四',
    time: '30分钟前',
    status: '成功'
  },
  {
    type: 'check',
    action: '创建盘点单',
    user: '王五',
    time: '1小时前',
    status: '成功'
  },
  {
    type: 'inbound',
    action: '入库单审核失败',
    user: '管理员',
    time: '2小时前',
    status: '失败'
  }
])

const formatNumber = (num: number) => {
  return num.toLocaleString()
}

const getActivityIcon = (type: string) => {
  const iconMap: Record<string, any> = {
    inbound: Upload,
    outbound: Download,
    stock: Refresh,
    check: Check
  }
  return iconMap[type] || Document
}

const handleQuickAction = (action: string) => {
  const actionMap: Record<string, string> = {
    inbound: '/inbound/order',
    outbound: '/outbound/order',
    stock: '/inventory/stock',
    report: '/report'
  }
  
  if (actionMap[action]) {
    router.push(actionMap[action])
  } else {
    ElMessage.info('功能开发中...')
  }
}
</script>

<style scoped>
.dashboard {
  max-width: var(--content-max-width);
  margin: 0 auto;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
}

.page-title {
  font-size: 32px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: 8px;
}

.page-subtitle {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 24px;
  margin-bottom: 32px;
}

.stat-card {
  background: var(--color-bg-primary);
  border-radius: var(--radius-xl);
  padding: 24px;
  box-shadow: var(--shadow-card);
  transition: all var(--duration-base) var(--ease-in-out);
  position: relative;
  overflow: hidden;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-card-hover);
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  opacity: 0;
  transition: opacity var(--duration-base) var(--ease-in-out);
}

.stat-card:hover::before {
  opacity: 1;
}

.stat-card-2::before {
  background: linear-gradient(90deg, #10B981 0%, #059669 100%);
}

.stat-card-3::before {
  background: linear-gradient(90deg, #F59E0B 0%, #D97706 100%);
}

.stat-card-4::before {
  background: linear-gradient(90deg, #EF4444 0%, #DC2626 100%);
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--color-primary);
}

.stat-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: 13px;
  font-weight: var(--font-weight-medium);
}

.trend-up {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.trend-down {
  background: rgba(239, 68, 68, 0.1);
  color: #EF4444;
}

.stat-content {
  margin-bottom: 16px;
}

.stat-value {
  font-size: 32px;
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.stat-label {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.stat-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 16px;
  border-top: 1px solid var(--color-border-primary);
  font-size: 13px;
}

.stat-compare {
  color: var(--color-text-tertiary);
}

.text-success {
  color: #10B981;
}

.text-danger {
  color: #EF4444;
}

.charts-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 24px;
  margin-bottom: 32px;
}

.chart-card {
  border-radius: var(--radius-xl);
}

.chart-card-large {
  grid-column: span 1;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.card-title h3 {
  font-size: 18px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.card-title p {
  font-size: 13px;
  color: var(--color-text-tertiary);
}

.chart-container {
  height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-placeholder {
  width: 100%;
  height: 100%;
}

.trend-chart {
  width: 100%;
  height: 100%;
}

.comparison-bars {
  width: 100%;
  padding: 0 20px;
}

.bar-item {
  margin-bottom: 24px;
}

.bar-item:last-child {
  margin-bottom: 0;
}

.bar-label {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: 8px;
}

.bar-wrapper {
  height: 12px;
  background: var(--color-bg-tertiary);
  border-radius: var(--radius-full);
  overflow: hidden;
  margin-bottom: 8px;
}

.bar {
  height: 100%;
  border-radius: var(--radius-full);
  transition: width var(--duration-slow) var(--ease-out);
}

.bar-inbound {
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
}

.bar-outbound {
  background: linear-gradient(90deg, #10B981 0%, #059669 100%);
}

.bar-transfer {
  background: linear-gradient(90deg, #F59E0B 0%, #D97706 100%);
}

.bar-check {
  background: linear-gradient(90deg, #8B5CF6 0%, #6366F1 100%);
}

.bar-value {
  font-size: 13px;
  color: var(--color-text-tertiary);
  text-align: right;
}

.warehouse-stats {
  width: 100%;
}

.warehouse-item {
  margin-bottom: 20px;
}

.warehouse-item:last-child {
  margin-bottom: 0;
}

.warehouse-info {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.warehouse-name {
  font-size: 14px;
  color: var(--color-text-secondary);
}

.warehouse-percent {
  font-size: 14px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
}

.bottom-section {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
}

.activity-card {
  border-radius: var(--radius-xl);
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.activity-item {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  transition: all var(--duration-fast) var(--ease-in-out);
}

.activity-item:hover {
  background: var(--color-bg-tertiary);
}

.activity-icon {
  width: 40px;
  height: 40px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.activity-icon-inbound {
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.activity-icon-outbound {
  background: rgba(16, 185, 129, 0.1);
  color: #10B981;
}

.activity-icon-stock {
  background: rgba(245, 158, 11, 0.1);
  color: #F59E0B;
}

.activity-icon-check {
  background: rgba(139, 92, 246, 0.1);
  color: #8B5CF6;
}

.activity-content {
  flex: 1;
}

.activity-title {
  font-size: 14px;
  color: var(--color-text-primary);
  margin-bottom: 4px;
}

.activity-meta {
  display: flex;
  gap: 12px;
  font-size: 12px;
  color: var(--color-text-tertiary);
}

.quick-actions-card {
  border-radius: var(--radius-xl);
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.action-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px 16px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--duration-fast) var(--ease-in-out);
}

.action-item:hover {
  background: var(--color-bg-tertiary);
  transform: translateY(-2px);
}

.action-icon {
  width: 56px;
  height: 56px;
  border-radius: var(--radius-lg);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
}

.action-icon-inbound {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.action-icon-outbound {
  background: linear-gradient(135deg, #10B981 0%, #059669 100%);
  color: white;
}

.action-icon-stock {
  background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
  color: white;
}

.action-icon-report {
  background: linear-gradient(135deg, #8B5CF6 0%, #6366F1 100%);
  color: white;
}

.action-label {
  font-size: 14px;
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .chart-card-large {
    grid-column: span 2;
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-card-large {
    grid-column: span 1;
  }
  
  .bottom-section {
    grid-template-columns: 1fr;
  }
}
</style>
