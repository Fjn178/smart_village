<template>
  <div class="home-container">
    <!-- 顶部导航 -->
    <div class="header">
      <div class="header-left">
        <h1>🌾 智慧乡村产业决策系统</h1>
      </div>
      <div class="header-right">
        <span class="user-info">欢迎，{{ userInfo?.username || '用户' }}（{{ roleMap[userInfo?.role] || '未知角色' }}）</span>
        <el-button type="danger" size="small" @click="handleLogout">退出登录</el-button>
      </div>
    </div>

    <!-- 功能卡片区 -->
    <div class="cards">
      <el-row :gutter="20">
        <!-- 村庄管理 -->
        <el-col :span="6">
          <el-card class="func-card" shadow="hover" @click="goTo('/villages')">
            <div class="card-icon">🏘️</div>
            <div class="card-title">村庄管理</div>
            <div class="card-desc">查看、新增、编辑、删除村庄信息</div>
          </el-card>
        </el-col>

        <!-- 产业诊断（预留入口） -->
        <el-col :span="6">
          <el-card class="func-card" shadow="hover" @click="goTo('/diagnose')">
            <div class="card-icon">📊</div>
            <div class="card-title">产业诊断</div>
            <div class="card-desc">分析村庄产业现状，诊断发展短板</div>
            <el-tag size="small" type="info">即将上线</el-tag>
          </el-card>
        </el-col>

        <!-- 产业推荐（预留入口） -->
        <el-col :span="6">
          <el-card class="func-card" shadow="hover" @click="goTo('/recommend')">
            <div class="card-icon">🎯</div>
            <div class="card-title">产业推荐</div>
            <div class="card-desc">基于相似案例，推荐适合的产业方向</div>
            <el-tag size="small" type="info">即将上线</el-tag>
          </el-card>
        </el-col>

        <!-- 报告生成（预留入口） -->
        <el-col :span="6">
          <el-card class="func-card" shadow="hover" @click="goTo('/report')">
            <div class="card-icon">📄</div>
            <div class="card-title">报告生成</div>
            <div class="card-desc">导出村庄诊断报告，用于申报或汇报</div>
            <el-tag size="small" type="info">即将上线</el-tag>
          </el-card>
        </el-col>
      </el-row>
    </div>

    <!-- 快捷信息 -->
    <div class="info-section">
      <el-card shadow="never">
        <template #header>
          <span>📋 快速开始</span>
        </template>
        <div class="quick-actions">
          <el-button type="primary" plain @click="goTo('/villages')">管理村庄</el-button>
          <el-button type="success" plain @click="goTo('/diagnose')">开始诊断</el-button>
          <el-button type="warning" plain @click="goTo('/recommend')">查看推荐</el-button>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import apiClient from '@/api/index'

const router = useRouter()

// 用户信息
const userInfo = ref(null)

// 角色映射
const roleMap = {
  admin: '系统管理员',
  town: '乡镇干部',
  village: '村支书'
}

// 获取当前用户信息
const fetchUserInfo = async () => {
  try {
    const res = await apiClient.get('/auth/me')
    if (res.data.code === 0) {
      userInfo.value = res.data.data
    }
  } catch (error) {
    console.error('获取用户信息失败:', error)
  }
}

// 退出登录
const handleLogout = () => {
  ElMessageBox.confirm('确定要退出登录吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(() => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('user_info')
    ElMessage.success('已退出')
    router.push('/login')
  }).catch(() => {})
}

// 页面跳转
const goTo = (path) => {
  router.push(path)
}

// 页面加载时获取用户信息
onMounted(() => {
  fetchUserInfo()
})
</script>

<style scoped>
.home-container {
  min-height: 100vh;
  background: #f0f2f5;
}

/* ===== 顶部导航 ===== */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 40px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  position: sticky;
  top: 0;
  z-index: 10;
}
.header-left h1 {
  font-size: 22px;
  margin: 0;
  color: #303133;
}
.header-right {
  display: flex;
  align-items: center;
  gap: 16px;
}
.user-info {
  font-size: 14px;
  color: #606266;
}

/* ===== 功能卡片 ===== */
.cards {
  padding: 30px 40px;
}
.func-card {
  text-align: center;
  padding: 20px 10px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}
.func-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
}
.card-icon {
  font-size: 48px;
  margin-bottom: 12px;
}
.card-title {
  font-size: 18px;
  font-weight: bold;
  color: #303133;
}
.card-desc {
  font-size: 13px;
  color: #909399;
  margin-top: 6px;
}

/* ===== 快捷信息 ===== */
.info-section {
  padding: 0 40px 30px 40px;
}
.quick-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
</style>
