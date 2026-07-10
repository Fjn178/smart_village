<template>
  <div class="upload-container">
    <!-- 页面标题 + 步骤引导 -->
    <div class="page-header">
      <h2>📤 村庄数据批量导入</h2>
      <p class="sub-title">按步骤操作，一次可导入多个村庄的完整数据</p>
    </div>

    <!-- 步骤引导卡片（纯提示，非表单步骤） -->
    <el-row :gutter="20" class="step-guide">
      <el-col :span="6">
        <div class="step-item">
          <span class="step-num">①</span>
          <span>下载模板</span>
          <el-tag size="small" type="info">.xlsx</el-tag>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="step-item">
          <span class="step-num">②</span>
          <span>按模板填写</span>
          <el-tag size="small" type="warning">含72项指标</el-tag>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="step-item">
          <span class="step-num">③</span>
          <span>上传文件</span>
          <el-tag size="small" type="success">≤10MB</el-tag>
        </div>
      </el-col>
      <el-col :span="6">
        <div class="step-item">
          <span class="step-num">④</span>
          <span>查看结果</span>
          <el-tag size="small" type="primary">自动校验</el-tag>
        </div>
      </el-col>
    </el-row>

    <!-- 核心操作区 -->
    <el-card class="upload-card" shadow="hover">
      <!-- 1. 模式选择 + 模板下载 -->
      <div class="toolbar">
        <el-radio-group v-model="importMode" size="default">
          <el-radio-button value="append">📥 追加导入（跳过已存在）</el-radio-button>
          <el-radio-button value="overwrite">🔄 覆盖导入（替换已存在）</el-radio-button>
        </el-radio-group>
        <el-button type="primary" plain @click="downloadTemplate">
          <el-icon><Download /></el-icon> 下载标准模板
        </el-button>
      </div>

      <!-- 2. 上传组件 -->
      <el-upload
        ref="uploadRef"
        class="upload-demo"
        drag
        :auto-upload="false"
        :limit="1"
        :on-change="handleFileChange"
        :on-remove="handleRemove"
        :on-exceed="handleExceed"
        accept=".xlsx,.xls"
        :file-list="fileList"
      >
        <el-icon class="el-icon--upload"><upload-filled /></el-icon>
        <div class="el-upload__text">
          拖拽 Excel 文件到这里，或 <em>点击选择文件</em>
        </div>
        <template #tip>
          <div class="el-upload__tip">
            仅支持 <el-tag size="small" type="danger">.xlsx</el-tag> / 
            <el-tag size="small" type="danger">.xls</el-tag>，文件大小不超过 10MB
          </div>
        </template>
      </el-upload>

      <!-- 3. 执行按钮 -->
      <div class="action-bar">
        <el-button 
          type="success" 
          size="large" 
          :disabled="!fileList.length || isUploading"
          :loading="isUploading"
          @click="startUpload"
        >
          {{ isUploading ? '导入中...' : '🚀 开始导入' }}
        </el-button>
        <span v-if="fileList.length" class="file-name">
          当前文件：{{ fileList[0].name }}
        </span>
      </div>

      <!-- 4. 进度展示 -->
      <div v-if="taskId && progressInfo.total > 0" class="progress-area">
        <el-divider />
        <div class="progress-header">
          <span>导入进度</span>
          <span>{{ progressInfo.current }} / {{ progressInfo.total }} 条 
            （{{ Math.round(progressInfo.current / progressInfo.total * 100) || 0 }}%）
          </span>
        </div>
        <el-progress 
          :percentage="Math.round(progressInfo.current / progressInfo.total * 100) || 0"
          :status="progressStatus"
          :stroke-width="20"
          striped
          striped-flow
        />
        <div class="status-text">
          <el-tag :type="statusTagType" size="large">
            {{ statusText }}
          </el-tag>
          <span v-if="progressInfo.error" class="error-msg">
            ❌ {{ progressInfo.error }}
          </span>
        </div>
      </div>

      <!-- 5. 错误详情表格（逐行展示） -->
      <div v-if="showErrorDetail" class="error-detail">
        <el-divider content-position="left">
          <span style="color: #f56c6c;">❌ 数据校验失败详情（请修正后重新上传）</span>
        </el-divider>
        <el-table :data="progressInfo.detail_errors" border stripe style="width: 100%">
          <el-table-column prop="row" label="Excel 行号" width="120" align="center" />
          <el-table-column label="错误内容" prop="errors">
            <template #default="scope">
              <ul style="margin: 4px 0; padding-left: 16px;">
                <li v-for="(err, idx) in scope.row.errors" :key="idx">{{ err }}</li>
              </ul>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 6. 成功完成提示 -->
      <el-alert
        v-if="isDone"
        title="✅ 数据导入完成！"
        type="success"
        description="所有村庄数据已成功入库，现在可以前往「产业诊断」模块查看结果。"
        show-icon
        :closable="false"
        style="margin-top: 20px;"
      />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, UploadFilled } from '@element-plus/icons-vue'
import axios from 'axios'

// ---------- 环境配置 ----------
// 请根据你的后端实际地址修改（.env 文件配置更好）
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'

// ---------- 状态变量 ----------
const importMode = ref('append')          // append / overwrite
const fileList = ref([])                 // 上传组件文件列表
const isUploading = ref(false)           // 是否正在上传/处理
const taskId = ref(null)                // 后台返回的任务ID
const progressInfo = ref({
  status: 'pending',   // pending, processing, done, fail
  total: 0,
  current: 0,
  error: '',
  detail_errors: []    // 逐行错误 [{row: 3, errors: ["年龄超限"]}]
})
let pollingTimer = null

// ---------- 计算属性 ----------
const isDone = computed(() => progressInfo.value.status === 'done')
const showErrorDetail = computed(() => 
  progressInfo.value.status === 'fail' && progressInfo.value.detail_errors?.length > 0
)

const progressStatus = computed(() => {
  const s = progressInfo.value.status
  if (s === 'done') return 'success'
  if (s === 'fail') return 'exception'
  if (s === 'processing') return ''  // 普通蓝色
  return ''  // pending
})

const statusTagType = computed(() => {
  const s = progressInfo.value.status
  if (s === 'done') return 'success'
  if (s === 'fail') return 'danger'
  if (s === 'processing') return 'warning'
  return 'info'
})

const statusText = computed(() => {
  const s = progressInfo.value.status
  if (s === 'done') return '✅ 导入成功'
  if (s === 'fail') return '❌ 导入失败'
  if (s === 'processing') return '⏳ 处理中...'
  return '⏸️ 排队等待'
})

// ---------- 方法 ----------
// 1. 下载模板
const downloadTemplate = async () => {
  try {
    const response = await axios.get(`${API_BASE}/api/data/template`, {
      responseType: 'blob'  // 关键：接收二进制文件
    })
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', '村庄数据导入模板.xlsx')
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    ElMessage.success('模板下载成功')
  } catch (error) {
    ElMessage.error('模板下载失败：' + (error.response?.data?.msg || error.message))
  }
}

// 2. 文件选择/变更
const handleFileChange = (uploadFile) => {
  // 校验文件大小（10MB）
  const isLt10M = uploadFile.size / 1024 / 1024 < 10
  if (!isLt10M) {
    ElMessage.error('文件大小不能超过 10MB！')
    fileList.value = []
    return false
  }
  // 直接替换（只允许一个文件）
  fileList.value = [uploadFile]
}

const handleRemove = () => {
  fileList.value = []
  // 清空旧任务状态
  resetTaskState()
}

const handleExceed = () => {
  ElMessage.warning('只允许上传一个文件，请先移除当前文件')
}

// 3. 开始上传
const startUpload = async () => {
  if (!fileList.value.length) {
    ElMessage.warning('请先选择 Excel 文件')
    return
  }

  const file = fileList.value[0].raw
  isUploading.value = true
  resetTaskState()  // 清空旧进度

  const formData = new FormData()
  formData.append('file', file)

  try {
    // 调用上传 API（mode 作为 query 参数）
    const response = await axios.post(`${API_BASE}/api/data/upload`, formData, {
      params: { mode: importMode.value },
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 30000
    })

    if (response.data.code === 200) {
      taskId.value = response.data.taskId
      ElMessage.success('文件已上传，后台开始处理...')
      // 开始轮询进度
      startPolling()
    } else {
      ElMessage.error('上传失败：' + response.data.msg)
      isUploading.value = false
    }
  } catch (error) {
    ElMessage.error('上传请求失败：' + (error.response?.data?.msg || error.message))
    isUploading.value = false
  }
}

// 4. 轮询进度
const startPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }

  pollingTimer = setInterval(async () => {
    if (!taskId.value) return

    try {
      const res = await axios.get(`${API_BASE}/api/data/task/${taskId.value}`)
      if (res.data.code === 200) {
        const data = res.data.data
        progressInfo.value = data

        // 如果任务结束（成功或失败），停止轮询
        if (data.status === 'done' || data.status === 'fail') {
          clearInterval(pollingTimer)
          pollingTimer = null
          isUploading.value = false
          
          if (data.status === 'done') {
            ElMessage.success(`导入完成！共处理 ${data.total} 条村庄数据。`)
          } else {
            ElMessage.error('导入失败，请查看下方的错误详情进行修正。')
          }
        }
      } else {
        // 任务不存在等情况
        clearInterval(pollingTimer)
        pollingTimer = null
        isUploading.value = false
        ElMessage.error('查询进度失败：' + res.data.msg)
      }
    } catch (err) {
      console.error('轮询出错：', err)
      // 不停止轮询，避免网络波动导致中断
    }
  }, 1500) // 1.5 秒查询一次
}

// 5. 重置状态
const resetTaskState = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
  taskId.value = null
  progressInfo.value = {
    status: 'pending',
    total: 0,
    current: 0,
    error: '',
    detail_errors: []
  }
  isUploading.value = false
}

// 组件销毁前清理定时器
onBeforeUnmount(() => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
})
</script>

<!-- ---------- 样式 ---------- -->
<style scoped>
.upload-container {
  max-width: 1100px;
  margin: 0 auto;
  padding: 30px 20px;
  font-size: 16px;  /* 大字号，适合基层干部 */
}

.page-header h2 {
  margin-bottom: 6px;
  color: #2c3e50;
}
.sub-title {
  color: #7f8c8d;
  font-size: 15px;
  margin-top: 0;
}

/* 步骤引导 */
.step-guide {
  margin: 24px 0 30px 0;
}
.step-item {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 14px 18px;
  display: flex;
  align-items: center;
  gap: 10px;
  border-left: 4px solid #409EFF;
  font-weight: 500;
}
.step-num {
  background: #409EFF;
  color: white;
  border-radius: 50%;
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
  flex-shrink: 0;
}

/* 卡片 */
.upload-card {
  padding: 10px 0;
}
.toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 28px;
  gap: 15px;
}
.upload-demo {
  margin: 20px 0 10px 0;
}
.action-bar {
  margin-top: 25px;
  display: flex;
  align-items: center;
  gap: 20px;
  flex-wrap: wrap;
}
.file-name {
  color: #409EFF;
  font-weight: 500;
  background: #ecf5ff;
  padding: 4px 16px;
  border-radius: 20px;
}

/* 进度 */
.progress-area {
  margin-top: 20px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 6px;
  font-weight: 500;
}
.status-text {
  margin-top: 14px;
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}
.error-msg {
  color: #f56c6c;
  background: #fef0f0;
  padding: 4px 14px;
  border-radius: 4px;
  font-size: 14px;
}

/* 错误详情表格 */
.error-detail {
  margin-top: 10px;
}
.error-detail ul {
  margin: 0;
  padding-left: 18px;
  list-style-type: disc;
}

/* 响应式适配（移动端） */
@media (max-width: 768px) {
  .step-guide .el-col {
    margin-bottom: 10px;
    flex: 0 0 50%;
    max-width: 50%;
  }
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  .action-bar {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>