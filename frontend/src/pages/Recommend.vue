<template>
  <div class="recommend-page">
    <el-card shadow="hover" class="recommend-card">
      <div class="page-header">
        <h2>📌 产业推荐结果</h2>
        <p>输入村庄信息后，自动获取最适合的产业推荐与匹配原因。</p>
      </div>

      <el-form :model="query" label-width="100px" class="search-form">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-form-item label="村庄名称">
              <el-input v-model="query.village_name" placeholder="必填或使用村庄ID" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="村庄ID">
              <el-input v-model="query.village_id" placeholder="可选：已知则优先查询" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="所属乡镇">
              <el-input v-model="query.town" placeholder="可帮助精确匹配" clearable />
            </el-form-item>
          </el-col>
          <el-col :span="4">
            <el-form-item label="推荐数量">
              <el-select v-model="query.top_n" placeholder="推荐个数">
                <el-option v-for="n in [1,2,3,4,5]" :key="n" :label="`${n}条`" :value="n" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="2" class="search-button-col">
            <el-button type="primary" size="medium" @click="fetchRecommend" :loading="loading" style="width: 100%;">
              查询
            </el-button>
          </el-col>
        </el-row>
      </el-form>

      <el-alert
        v-if="errorMsg"
        title="查询失败"
        type="error"
        :description="errorMsg"
        show-icon
        class="mt-20"
      />
    </el-card>

    <div v-if="loading" class="loading-placeholder">
      <el-skeleton :rows="4" />
    </div>

    <div v-if="hasResult" class="result-section">
      <el-card shadow="hover" class="result-summary">
        <div class="summary-title">基础信息</div>
        <el-row :gutter="20">
          <el-col :span="8"><strong>村庄名称：</strong>{{ result.village_name || '-' }}</el-col>
          <el-col :span="8"><strong>村庄ID：</strong>{{ result.village_id || '-' }}</el-col>
          <el-col :span="8"><strong>所属乡镇：</strong>{{ result.town || '-' }}</el-col>
        </el-row>
      </el-card>

      <el-row :gutter="20" class="recommend-list" v-if="result.recommendations?.length">
        <el-col :span="8" v-for="item in result.recommendations" :key="item.industry">
          <el-card shadow="always" class="industry-card">
            <div class="industry-head">
              <div>
                <h3>{{ item.industry }}</h3>
                <p class="industry-score">匹配度 {{ formatScore(item.score) }}</p>
              </div>
            </div>
            <div class="industry-description">{{ item.description }}</div>
            <el-divider />
            <div class="industry-detail">
              <div class="detail-title">匹配指标</div>
              <div v-if="item.matched_indicators?.length">
                <el-tag
                  v-for="(indicator, idx) in item.matched_indicators"
                  :key="idx"
                  type="success"
                  class="detail-tag"
                >
                  {{ indicator }}
                </el-tag>
              </div>
              <div v-else class="no-indicators">暂无匹配指标</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card v-if="result.recommendations?.length === 0" shadow="hover" class="no-result-card">
        <p>当前村庄尚无可用指标或未匹配到推荐结果，请检查村庄信息或先上传数据。</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed } from 'vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'

const query = reactive({
  village_id: '',
  village_name: '',
  town: '',
  top_n: 3
})
const loading = ref(false)
const result = ref(null)
const errorMsg = ref('')

const hasResult = computed(() => result.value && Object.keys(result.value).length > 0)

const fetchRecommend = async () => {
  errorMsg.value = ''
  result.value = null

  if (!query.village_id && !query.village_name) {
    errorMsg.value = '请输入村庄名称或村庄ID。'
    return
  }

  loading.value = true
  try {
    const params = {
      top_n: query.top_n,
      ...(query.village_id ? { village_id: query.village_id } : { village_name: query.village_name }),
      ...(query.town ? { town: query.town } : {})
    }
    const response = await axios.get(`${API_BASE}/api/recommend/industry`, { params })
    const data = response.data

    if (data?.code === 200 && data.data) {
      result.value = data.data
      if (!result.value.recommendations || !result.value.recommendations.length) {
        errorMsg.value = '未找到匹配的推荐结果。'
      }
    } else {
      errorMsg.value = data?.msg || '推荐查询失败，请稍后重试。'
    }
  } catch (error) {
    errorMsg.value = error.response?.data?.msg || error.message || '网络请求失败。'
  } finally {
    loading.value = false
  }
}

const formatScore = (score) => {
  const numeric = Number(score) || 0
  return `${(numeric * 100).toFixed(1)}%`
}
</script>

<style scoped>
.recommend-page {
  padding: 24px;
}
.page-header h2 {
  margin: 0;
  font-size: 24px;
}
.page-header p {
  margin: 8px 0 0;
  color: #606266;
}
.search-form {
  margin-top: 20px;
}
.search-button-col {
  display: flex;
  align-items: flex-end;
}
.search-button-col .el-form-item {
  margin-bottom: 0;
}
.loading-placeholder {
  margin-top: 20px;
}
.result-section {
  margin-top: 24px;
}
.result-summary {
  margin-bottom: 20px;
}
.industry-card {
  min-height: 260px;
}
.industry-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.industry-head h3 {
  margin: 0;
  font-size: 18px;
}
.industry-score {
  margin: 4px 0 0;
  color: #409eff;
  font-weight: 600;
}
.industry-description {
  color: #606266;
  line-height: 1.7;
}
.detail-title {
  margin-bottom: 8px;
  font-weight: 600;
  color: #303133;
}
.detail-tag {
  margin-bottom: 8px;
  margin-right: 8px;
}
.no-indicators {
  color: #909399;
}
.mt-20 {
  margin-top: 20px;
}
</style>
