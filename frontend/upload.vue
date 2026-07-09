<template>
  <div style="padding: 40px; max-width: 600px; margin: 0 auto;">
    <h2>📤 Excel 批量导入</h2>

    <!-- 上传区域 -->
    <input
      type="file"
      accept=".xlsx,.xls"
      ref="fileInput"
      @change="handleFileChange"
      style="display: none"
    />
    <button @click="triggerUpload" :disabled="isUploading" style="padding: 10px 20px; cursor: pointer;">
      {{ isUploading ? '上传中...' : '选择 Excel 文件' }}
    </button>
    <span v-if="fileName" style="margin-left: 15px; color: #409EFF;">{{ fileName }}</span>

    <!-- 上传阶段错误提示 -->
    <div v-if="uploadError" style="margin-top: 15px; color: #F56C6C; background: #ffe6e6; padding: 10px; border-radius: 4px;">
      ❌ {{ uploadError }}
    </div>

    <!-- 进度条展示（仅在 taskId 存在且 total > 0 或出错时显示） -->
    <div v-if="taskId && (progressInfo.total > 0 || progressInfo.status === 'fail')" style="margin-top: 30px; border: 1px solid #eee; padding: 20px; border-radius: 8px;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
        <span>导入进度</span>
        <span>
          {{ progressInfo.current }} / {{ progressInfo.total }}
          ({{ progressInfo.total > 0 ? Math.round((progressInfo.current / progressInfo.total) * 100) : 0 }}%)
        </span>
      </div>

      <!-- 进度条 -->
      <div style="width: 100%; background-color: #f3f3f3; border-radius: 6px; overflow: hidden; height: 24px;">
        <div
          :style="{
            width: (progressInfo.total > 0 ? (progressInfo.current / progressInfo.total * 100) : 0) + '%',
            height: '100%',
            backgroundColor: statusColor,
            transition: 'width 0.3s ease',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            fontSize: '14px'
          }"
        >
          {{ statusText }}
        </div>
      </div>

      <!-- 进度中或完成后的错误信息 -->
      <div v-if="progressInfo.error" style="margin-top: 10px; color: red; background: #ffe6e6; padding: 10px; border-radius: 4px;">
        ❌ 错误：{{ progressInfo.error }}
      </div>
    </div>

    <!-- 成功提示 -->
    <div v-if="isDone" style="margin-top: 20px; color: #67C23A; font-weight: bold;">
      ✅ 导入完成！共导入 {{ progressInfo.total }} 条数据
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onUnmounted } from 'vue'
import axios from 'axios' // 需执行 npm install axios

// ✅ 使用环境变量，支持多环境部署（开发/生产）
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

const fileInput = ref(null)
const fileName = ref('')
const isUploading = ref(false)
const taskId = ref(null)
const progressInfo = ref({ status: 'pending', total: 0, current: 0, error: '' })
const uploadError = ref('') // 上传阶段错误信息

let pollingTimer = null
let abortController = null // 用于取消上传和轮询请求

// --- 状态派生 ---
const statusColor = computed(() => {
  const status = progressInfo.value.status
  if (status === 'done') return '#67C23A'
  if (status === 'fail') return '#F56C6C'
  if (status === 'processing') return '#409EFF'
  return '#E6A23C'
})

const statusText = computed(() => {
  const status = progressInfo.value.status
  if (status === 'done') return '导入成功'
  if (status === 'fail') return '导入失败'
  if (status === 'processing') return '处理中...'
  if (status === 'pending') return '排队中...'
  return '等待开始'
})

const isDone = computed(() => progressInfo.value.status === 'done')

// --- 工具函数：清理由定时器和请求控制器 ---
const clearPolling = () => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
  isUploading.value = false
  // 允许再次选择同一个文件（重置 input）
  if (fileInput.value) fileInput.value.value = ''
}

// --- 触发文件选择 ---
const triggerUpload = () => {
  if (isUploading.value) return
  // 清除上次的错误提示
  uploadError.value = ''
  fileInput.value.click()
}

// --- 开始轮询进度（带失败重试上限） ---
const startPolling = () => {
  let failCount = 0
  const MAX_FAIL = 3

  pollingTimer = setInterval(async () => {
    try {
      const progressRes = await axios.get(
        `${API_BASE}/api/data/task/${taskId.value}`,
        { signal: abortController?.signal } // 可通过 AbortController 取消
      )
      failCount = 0 // 成功后重置失败计数
      progressInfo.value = progressRes.data

      // 任务终态：成功或失败，停止轮询
      if (progressRes.data.status === 'done' || progressRes.data.status === 'fail') {
        clearPolling()
      }
    } catch (err) {
      // 如果是主动取消的请求，直接退出
      if (axios.isCancel(err)) return

      failCount++
      if (failCount >= MAX_FAIL) {
        // 超过最大重试次数，标记失败并停止
        progressInfo.value = {
          ...progressInfo.value,
          status: 'fail',
          error: '获取进度失败，请检查网络后重试'
        }
        clearPolling()
      }
    }
  }, 1000)
}

// --- 选择文件后的处理流程 ---
const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  // 重置状态
  fileName.value = file.name
  isUploading.value = true
  uploadError.value = ''

  // 取消上一次未完成的请求和轮询
  if (abortController) abortController.abort()
  abortController = new AbortController()

  // 清除旧进度和定时器
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
  taskId.value = null
  progressInfo.value = { status: 'pending', total: 0, current: 0, error: '' }

  try {
    // 1. 上传文件
    const formData = new FormData()
    formData.append('file', file)

    const uploadRes = await axios.post(`${API_BASE}/api/data/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      signal: abortController.signal // 支持取消
    })

    taskId.value = uploadRes.data.taskId
    console.log('任务已创建，ID:', taskId.value)

    // 2. 开始轮询
    startPolling()

  } catch (error) {
    // 如果是取消请求导致的错误，不提示用户
    if (axios.isCancel(error)) return

    console.error('上传失败:', error)
    const errMsg = error.response?.data?.detail || error.message || '上传失败'
    uploadError.value = errMsg
    isUploading.value = false
    if (fileInput.value) fileInput.value.value = ''
  }
}

// --- 组件卸载时彻底清理 ---
onUnmounted(() => {
  if (pollingTimer) clearInterval(pollingTimer)
  if (abortController) abortController.abort() // 取消所有未完成的 HTTP 请求
})
</script>
