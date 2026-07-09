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

    <!-- 进度条展示 -->
    <div v-if="taskId && progressInfo.total > 0" style="margin-top: 30px; border: 1px solid #eee; padding: 20px; border-radius: 8px;">
      <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
        <span>导入进度</span>
        <span>{{ progressInfo.current }} / {{ progressInfo.total }} ({{ Math.round(progressInfo.current / progressInfo.total * 100) || 0 }}%)</span>
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
import axios from 'axios'  // 需执行：npm install axios

// API 基础地址（改为你后端实际地址）
const API_BASE = 'http://127.0.0.1:8000'

const fileInput = ref(null)
const fileName = ref('')
const isUploading = ref(false)
const taskId = ref(null)
const progressInfo = ref({ status: 'pending', total: 0, current: 0, error: '' })
let pollingTimer = null

// 计算属性：状态颜色
const statusColor = computed(() => {
  const status = progressInfo.value.status
  if (status === 'done') return '#67C23A'
  if (status === 'fail') return '#F56C6C'
  if (status === 'processing') return '#409EFF'
  return '#E6A23C' // pending
})

// 计算属性：状态文字
const statusText = computed(() => {
  const status = progressInfo.value.status
  if (status === 'done') return '导入成功'
  if (status === 'fail') return '导入失败'
  if (status === 'processing') return '处理中...'
  if (status === 'pending') return '排队中...'
  return '等待开始'
})

const isDone = computed(() => progressInfo.value.status === 'done')

// 触发文件选择框
const triggerUpload = () => {
  if (isUploading.value) return
  fileInput.value.click()
}

// 选择文件后的处理
const handleFileChange = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  fileName.value = file.name
  isUploading.value = true
  
  // 重置旧状态
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
  progressInfo.value = { status: 'pending', total: 0, current: 0, error: '' }

  try {
    // 1. 调用上传API
    const formData = new FormData()
    formData.append('file', file)
    
    const uploadRes = await axios.post(`${API_BASE}/api/data/upload`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    
    taskId.value = uploadRes.data.taskId
    console.log('任务已创建，ID:', taskId.value)

    // 2. 开始轮询进度（每1秒查一次）
    pollingTimer = setInterval(async () => {
      try {
        const progressRes = await axios.get(`${API_BASE}/api/data/task/${taskId.value}`)
        progressInfo.value = progressRes.data
        
        // 如果任务结束（成功或失败），停止轮询
        if (progressRes.data.status === 'done' || progressRes.data.status === 'fail') {
          clearInterval(pollingTimer)
          pollingTimer = null
          isUploading.value = false
          // 清空input，允许重新上传同一个文件
          fileInput.value.value = ''
        }
      } catch (err) {
        console.error('轮询进度失败:', err)
      }
    }, 1000)

  } catch (error) {
    console.error('上传失败:', error)
    alert('上传失败: ' + (error.response?.data?.detail || error.message))
    isUploading.value = false
    fileInput.value.value = ''
  }
}

// 组件销毁时清除定时器
onUnmounted(() => {
  if (pollingTimer) {
    clearInterval(pollingTimer)
    pollingTimer = null
  }
})
</script>
