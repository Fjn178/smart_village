<template>
  <div class="village-container">
    <div class="header">
      <h2>村庄管理</h2>
      <el-button type="primary" @click="handleAdd">+ 新增村庄</el-button>
    </div>

    <!-- 表格 -->
    <el-table :data="tableData" v-loading="loading" border style="width: 100%">
      <el-table-column prop="id" label="ID" width="80" />
      <el-table-column prop="name" label="村庄名称" width="130" />
      <el-table-column prop="province" label="省份" width="100" />
      <el-table-column prop="city" label="城市" width="100" />
      <el-table-column prop="county" label="区县" width="110" />
      <el-table-column prop="town" label="乡镇" width="130" />
      <el-table-column prop="population" label="人口" width="100" />
      <el-table-column prop="area" label="面积(亩)" width="110" />
      <el-table-column label="操作" width="180" fixed="right">
        <template #default="{ row }">
          <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
          <el-button type="danger" size="small" @click="handleDelete(row.id)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- ===== 新增/编辑弹窗 ===== -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="村庄名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入村庄名称" />
        </el-form-item>
        <el-form-item label="省份" prop="province">
          <el-input v-model="form.province" placeholder="请输入省份" />
        </el-form-item>
        <el-form-item label="城市" prop="city">
          <el-input v-model="form.city" placeholder="请输入城市" />
        </el-form-item>
        <el-form-item label="区县" prop="county">
          <el-input v-model="form.county" placeholder="请输入区县" />
        </el-form-item>
        <el-form-item label="乡镇" prop="town">
          <el-input v-model="form.town" placeholder="请输入乡镇" />
        </el-form-item>
        <el-form-item label="人口" prop="population">
          <el-input-number v-model="form.population" :min="0" style="width: 100%" />
        </el-form-item>
        <el-form-item label="面积(亩)" prop="area">
          <el-input-number v-model="form.area" :min="0" :precision="1" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { villageApi } from '@/api/village'

// ===== 状态 =====
const loading = ref(false)
const tableData = ref([])
const dialogVisible = ref(false)
const dialogType = ref('add') // 'add' 或 'edit'
const submitLoading = ref(false)
const formRef = ref()
const dialogTitle = ref('')

const form = reactive({
  id: null,
  name: '',
  province: '',
  city: '',
  county: '',
  town: '',
  population: 0,
  area: 0
})

const rules = {
  name: [{ required: true, message: '请输入村庄名称', trigger: 'blur' }],
  province: [{ required: true, message: '请输入省份', trigger: 'blur' }],
  city: [{ required: true, message: '请输入城市', trigger: 'blur' }]
}

// ===== 获取列表数据 =====
const fetchData = async () => {
  loading.value = true
  try {
    const res = await villageApi.getList()
    if (res.data.code === 0) {
      tableData.value = res.data.data || []
    } else {
      ElMessage.error(res.data.msg || '获取列表失败')
    }
  } catch (error) {
    ElMessage.error('请求失败，请检查后端是否运行')
  } finally {
    loading.value = false
  }
}

// ===== 重置表单 =====
const resetForm = () => {
  form.id = null
  form.name = ''
  form.province = ''
  form.city = ''
  form.county = ''
  form.town = ''
  form.population = 0
  form.area = 0
  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

// ===== 新增 =====
const handleAdd = () => {
  dialogType.value = 'add'
  dialogTitle.value = '新增村庄'
  resetForm()
  dialogVisible.value = true
}

// ===== 编辑 =====
const handleEdit = (row) => {
  dialogType.value = 'edit'
  dialogTitle.value = '编辑村庄'
  Object.assign(form, row)
  dialogVisible.value = true
}

// ===== 删除 =====
const handleDelete = (id) => {
  ElMessageBox.confirm('确定要删除该村庄吗？', '提示', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    type: 'warning'
  }).then(async () => {
    try {
      const res = await villageApi.delete(id)
      if (res.data.code === 0) {
        ElMessage.success('删除成功')
        fetchData()
      } else {
        ElMessage.error(res.data.msg || '删除失败')
      }
    } catch (error) {
      ElMessage.error('删除失败，请稍后重试')
    }
  }).catch(() => {})
}

// ===== 提交表单（新增/编辑） =====
const submitForm = async () => {
  if (!formRef.value) return
  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      let res
      if (dialogType.value === 'add') {
        res = await villageApi.create(form)
      } else {
        res = await villageApi.update(form.id, form)
      }
      if (res.data.code === 0) {
        ElMessage.success(dialogType.value === 'add' ? '新增成功' : '更新成功')
        dialogVisible.value = false
        fetchData()
      } else {
        ElMessage.error(res.data.msg || '操作失败')
      }
    } catch (error) {
      ElMessage.error('请求失败，请检查网络')
    } finally {
      submitLoading.value = false
    }
  })
}

// ===== 页面加载时自动获取数据 =====
onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.village-container {
  padding: 20px;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}
.header h2 {
  margin: 0;
}
</style>