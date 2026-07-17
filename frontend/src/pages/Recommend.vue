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
            <el-form-item label="展示数量">
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

      <el-alert v-if="errorMsg" title="查询失败" type="error" :description="errorMsg" show-icon class="mt-20" />
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

      <el-card shadow="hover" class="recommend-showcase" v-if="recommendationList.length">
        <div class="showcase-header">
          <div>
            <h3>推荐案例库</h3>
            <p>以下是根据当前村庄指标计算出的优先案例，点击任一案例即可查看详细说明。</p>
          </div>
          <div class="showcase-tip">已匹配 {{ recommendationList.length }} 个重点方向</div>
        </div>

        <div class="case-strip">
          <div
            v-for="(item, index) in recommendationList"
            :key="`${item.industry}-${index}`"
            class="case-card"
            :class="{ active: selectedIndex === index }"
            @click="selectRecommendation(index)"
            role="button"
            tabindex="0"
            @keydown.enter.prevent="selectRecommendation(index)"
          >
            <div class="case-rank">{{ index + 1 }}</div>
            <div class="case-name">{{ item.industry }}</div>
            <div class="case-score">匹配度 {{ formatScore(item.score) }}</div>
            <div class="case-preview">{{ item.description }}</div>
            <div class="case-action">点击查看详情</div>
          </div>
        </div>

        <div v-if="activeRecommendation" class="case-detail-panel">
          <div class="detail-header">
            <div>
              <h4>{{ activeRecommendation.industry }}</h4>
              <p>{{ activeRecommendation.description }}</p>
            </div>
            <div class="detail-badge">当前案例</div>
          </div>

          <div class="detail-brief">
            <div class="brief-item">
              <span class="brief-label">匹配度</span>
              <strong>{{ formatScore(activeRecommendation.score) }}</strong>
            </div>
            <div class="brief-item">
              <span class="brief-label">核心指标</span>
              <strong>{{ activeIndicatorSummary }}</strong>
            </div>
          </div>

          <div class="module-nav" role="tablist">
            <button
              v-for="(module, moduleIndex) in modules"
              :key="module.title"
              class="module-tab"
              :class="{ active: selectedModule === moduleIndex }"
              @click="selectedModule = moduleIndex"
            >
              {{ module.title }}
            </button>
          </div>

          <div class="module-content">
            <h5>{{ activeModule.title }}</h5>
            <p>{{ activeModule.content }}</p>
          </div>
        </div>
      </el-card>

      <el-card v-if="result.recommendations?.length === 0" shadow="hover" class="no-result-card">
        <p>当前村庄尚无可用指标或未匹配到推荐结果，请检查村庄信息或先上传数据。</p>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { reactive, ref, computed, watch } from 'vue'
import axios from 'axios'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:5000'

const query = reactive({
  village_id: '',
  village_name: '',
  town: '',
  top_n: 5
})
const loading = ref(false)
const result = ref(null)
const errorMsg = ref('')
const selectedIndex = ref(0)
const selectedModule = ref(0)

const hasResult = computed(() => result.value && Object.keys(result.value).length > 0)
const recommendationList = computed(() => result.value?.recommendations || [])
const activeRecommendation = computed(() => recommendationList.value[selectedIndex.value] || null)
const activeIndicatorSummary = computed(() => {
  const indicators = activeRecommendation.value?.matched_indicators || []
  return indicators.length ? indicators.slice(0, 3).join(' · ') : '暂无明显匹配指标'
})
const modules = [
  { title: '产业定位' },
  { title: '适配理由' },
  { title: '实施路径' },
  { title: '收益预期' },
  { title: '风险提示' },
  { title: '配套建议' }
]
const activeModule = computed(() => getModuleContent(activeRecommendation.value, selectedModule.value))

watch(result, () => {
  selectedIndex.value = 0
  selectedModule.value = 0
})

const selectRecommendation = (index) => {
  selectedIndex.value = index
  selectedModule.value = 0
}

const normalizeRecommendations = (payload) => {
  if (!payload) return []
  const recommendations = payload.recommendations || payload.cases || []
  return Array.isArray(recommendations) ? recommendations : []
}

const fetchRecommend = async () => {
  errorMsg.value = ''
  result.value = null

  const villageId = query.village_id?.trim()
  const villageName = query.village_name?.trim()
  const town = query.town?.trim()

  if (!villageId && !villageName) {
    errorMsg.value = '请输入村庄ID或村庄名称。'
    return
  }

  loading.value = true
  try {
    let data = null

    if (villageId) {
      try {
        const response = await axios.get(`${API_BASE}/api/cases/match/${encodeURIComponent(villageId)}`)
        data = response.data
      } catch (error) {
        data = null
      }
    }

    if (!data || data.code !== 200 || !data.data) {
      const params = {
        top_n: Math.min(Number(query.top_n) || 5, 5),
        ...(villageId ? { village_id: villageId } : { village_name: villageName }),
        ...(town ? { town } : {})
      }
      const fallbackResponse = await axios.get(`${API_BASE}/api/recommend/industry`, { params })
      data = fallbackResponse.data
    }

    if (data?.code === 200 && data.data) {
      const payload = data.data
      const recommendations = normalizeRecommendations(payload)

      result.value = {
        village_id: payload.village_id || payload.villageId || villageId || '',
        village_name: payload.village_name || payload.villageName || villageName || '',
        town: payload.town || town || '',
        recommendations
      }

      if (!recommendations.length) {
        errorMsg.value = '未找到匹配的推荐结果。'
      }
    } else {
      errorMsg.value = data?.msg || '案例匹配查询失败，请稍后重试。'
    }
  } catch (error) {
    errorMsg.value = error.response?.data?.msg || error.message || '网络请求失败。'
  } finally {
    loading.value = false
  }
}

const getModuleContent = (item, moduleIndex) => {
  if (!item) {
    return {
      title: '案例说明',
      content: '请选择一个案例查看详细说明。'
    }
  }

  const indicators = (item.matched_indicators || []).slice(0, 3).join('、') || '暂无明显匹配指标'
  const modulesContent = [
    {
      title: '产业定位',
      content: `${item.industry}适合作为当前村庄的优先发展方向。${item.description}`
    },
    {
      title: '适配理由',
      content: `根据当前村庄的基础指标，${indicators}等信息对该方向的支撑比较明显，说明其具备较高的落地匹配度。`
    },
    {
      title: '实施路径',
      content: '建议从资源盘点、试点示范和品牌输出三个阶段推进，优先把村庄现有资源打造成可复制的产业闭环。'
    },
    {
      title: '收益预期',
      content: '通过产业链延伸、产品升级和服务配套，可提升土地和人力资源的使用效率，并带动村集体收益和周边就业。'
    },
    {
      title: '风险提示',
      content: '需要关注市场波动、技术门槛和运营经验不足等风险，建议先从小范围试点逐步扩大。'
    },
    {
      title: '配套建议',
      content: '可同步整合政策扶持、培训服务、物流和宣传推广资源，提升产业落地速度和稳定性。'
    }
  ]

  return modulesContent[moduleIndex] || modulesContent[0]
}

const formatScore = (score) => {
  const numeric = Number(score) || 0
  return `${(numeric * 100).toFixed(1)}%`
}
</script>

<style scoped>
.recommend-page { padding: 24px; }
.page-header h2 { margin: 0; font-size: 24px; }
.page-header p { margin: 8px 0 0; color: #606266; }
.search-form { margin-top: 20px; }
.search-button-col { display: flex; align-items: flex-end; }
.search-button-col .el-form-item { margin-bottom: 0; }
.loading-placeholder { margin-top: 20px; }
.result-section { margin-top: 24px; }
.result-summary { margin-bottom: 20px; }
.recommend-showcase { margin-top: 8px; }
.showcase-header { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; margin-bottom: 16px; }
.showcase-header h3 { margin: 0; font-size: 18px; }
.showcase-header p { margin: 6px 0 0; color: #606266; }
.showcase-tip { color: #409eff; font-size: 13px; white-space: nowrap; }
.case-strip { display: flex; gap: 12px; overflow-x: auto; padding: 4px 2px 8px; }
.case-card { flex: 0 0 240px; padding: 16px; border: 1px solid #e4e7ed; border-radius: 14px; background: linear-gradient(135deg, #ffffff 0%, #f6fbff 100%); cursor: pointer; transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease; animation: caseFadeIn 0.45s ease both; min-height: 160px; }
.case-card:hover { transform: translateY(-2px); box-shadow: 0 8px 20px rgba(64, 158, 255, 0.12); }
.case-card.active { border-color: #409eff; box-shadow: 0 10px 24px rgba(64, 158, 255, 0.18); transform: translateY(-2px); }
.case-rank { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 50%; background: #ecf5ff; color: #409eff; font-weight: 700; margin-bottom: 10px; }
.case-name { font-size: 16px; font-weight: 700; color: #303133; margin-bottom: 6px; }
.case-score { color: #409eff; font-weight: 600; margin-bottom: 8px; }
.case-preview { color: #606266; line-height: 1.6; font-size: 13px; }
.case-detail-panel { margin-top: 18px; border: 1px solid #ebeef5; border-radius: 14px; padding: 18px; background: #f8fbff; }
.detail-header { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.detail-header h4 { margin: 0; font-size: 18px; }
.detail-header p { margin: 6px 0 0; color: #606266; }
.detail-badge { padding: 6px 10px; border-radius: 999px; background: #409eff; color: #fff; font-size: 12px; white-space: nowrap; }
.detail-brief { display: flex; flex-wrap: wrap; gap: 12px; margin: 16px 0; }
.brief-item { display: flex; flex-direction: column; gap: 4px; padding: 10px 12px; border-radius: 10px; background: #fff; border: 1px solid #e4e7ed; min-width: 220px; }
.brief-label { color: #909399; font-size: 12px; }
.module-nav { display: flex; gap: 8px; overflow-x: auto; padding-bottom: 4px; margin-bottom: 12px; }
.module-tab { border: 1px solid #d9ecff; background: #fff; color: #409eff; padding: 8px 12px; border-radius: 999px; white-space: nowrap; cursor: pointer; }
.module-tab.active { background: #409eff; color: #fff; border-color: #409eff; }
.module-content { background: #fff; border: 1px solid #ebeef5; border-radius: 12px; padding: 14px 16px; }
.module-content h5 { margin: 0 0 8px; font-size: 16px; }
.module-content p { margin: 0; color: #606266; line-height: 1.8; }
.mt-20 { margin-top: 20px; }
.case-action { margin-top: 10px; color: #409eff; font-size: 12px; font-weight: 600; }
.case-card.active .case-rank { background: #409eff; color: #fff; }
.case-card.active .case-action { color: #337ecc; }
.case-strip { scroll-snap-type: x proximity; }
.case-card { scroll-snap-align: start; }
@keyframes caseFadeIn { from { opacity: 0; transform: translateY(10px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
</style>
