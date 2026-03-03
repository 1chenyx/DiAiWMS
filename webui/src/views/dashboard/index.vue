<template>
  <div class="dashboard">
    <h1>仪表盘</h1>
    
    <!-- 统计卡片 -->
    <div class="stats-cards">
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-number">1,234</div>
          <div class="stat-label">库存总量</div>
        </div>
        <el-icon class="stat-icon"><Box /></el-icon>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-number">56</div>
          <div class="stat-label">今日入库</div>
        </div>
        <el-icon class="stat-icon"><ArrowUp /></el-icon>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-number">89</div>
          <div class="stat-label">今日出库</div>
        </div>
        <el-icon class="stat-icon"><ArrowDown /></el-icon>
      </el-card>
      
      <el-card shadow="hover" class="stat-card">
        <div class="stat-content">
          <div class="stat-number">12</div>
          <div class="stat-label">待处理任务</div>
        </div>
        <el-icon class="stat-icon"><Timer /></el-icon>
      </el-card>
    </div>
    
    <!-- 图表区域 -->
    <div class="charts-section">
      <el-card shadow="hover" class="chart-card">
        <template #header>
          <div class="card-header">
            <span>库存趋势</span>
          </div>
        </template>
        <div class="chart-container">
          <!-- 这里可以集成ECharts等图表库 -->
          <div class="placeholder-chart">库存趋势图表</div>
        </div>
      </el-card>
      
      <el-card shadow="hover" class="chart-card">
        <template #header>
          <div class="card-header">
            <span>入库出库对比</span>
          </div>
        </template>
        <div class="chart-container">
          <!-- 这里可以集成ECharts等图表库 -->
          <div class="placeholder-chart">入库出库对比图表</div>
        </div>
      </el-card>
    </div>
    
    <!-- 最近操作 -->
    <el-card shadow="hover" class="recent-activities">
      <template #header>
        <div class="card-header">
          <span>最近操作</span>
        </div>
      </template>
      <el-table :data="recentActivities" style="width: 100%">
        <el-table-column prop="time" label="时间" width="180" />
        <el-table-column prop="user" label="操作人" width="120" />
        <el-table-column prop="action" label="操作" />
        <el-table-column prop="status" label="状态" width="80">
          <template #default="scope">
            <el-tag :type="scope.row.status === '成功' ? 'success' : 'danger'">
              {{ scope.row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Box, ArrowUp, ArrowDown, Timer } from '@element-plus/icons-vue'

// 模拟最近操作数据
const recentActivities = ref([
  {
    time: '2026-02-28 17:30',
    user: '管理员',
    action: '创建入库单 ASN-20260228-001',
    status: '成功'
  },
  {
    time: '2026-02-28 16:45',
    user: '张三',
    action: '完成出库操作',
    status: '成功'
  },
  {
    time: '2026-02-28 15:20',
    user: '李四',
    action: '调整库存 SKU001',
    status: '成功'
  },
  {
    time: '2026-02-28 14:10',
    user: '王五',
    action: '创建盘点单',
    status: '成功'
  },
  {
    time: '2026-02-28 13:05',
    user: '管理员',
    action: '添加新用户',
    status: '成功'
  }
])
</script>

<style scoped>
.dashboard {
  padding: 20px 0;
}

.dashboard h1 {
  margin: 0 0 30px 0;
  font-size: 24px;
  color: #303133;
}

.stats-cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  position: relative;
  overflow: hidden;
}

.stat-content {
  padding: 20px;
}

.stat-number {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
  margin-bottom: 10px;
}

.stat-label {
  font-size: 14px;
  color: #909399;
}

.stat-icon {
  position: absolute;
  top: 20px;
  right: 20px;
  font-size: 48px;
  color: rgba(0, 0, 0, 0.05);
}

.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.chart-card {
  height: 300px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: calc(100% - 48px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-chart {
  color: #909399;
  font-size: 16px;
}

.recent-activities {
  margin-top: 20px;
}
</style>
