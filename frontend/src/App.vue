<template>
  <div class="container">
    <h1>排课组 - 本地开发子系统</h1>
    <p class="hint">将调用 base 服务获取教师信息，再写入排课数据库</p>
    <button @click="createSchedule" :disabled="loading">为教师 #1001 排课</button>

    <div v-if="loading" class="status">请求中...</div>
    <div v-if="result" class="result">
      <p>排课 ID：{{ result.schedule_id }}</p>
      <p>教师：{{ result.teacher_name }}</p>
      <p>课程：{{ result.course }}</p>
      <p>状态：{{ result.message }}</p>
    </div>
    <div v-if="error" class="error">错误：{{ error }}</div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const loading = ref(false)
const result  = ref(null)
const error   = ref(null)

async function createSchedule() {
  loading.value = true
  result.value  = null
  error.value   = null
  try {
    // 【规范2：流量路由规范】只写相对路径
    // 本地：Vite proxy 转到 http://127.0.0.1:8082
    // 大盘：Nginx 转发 /api/course/ -> http://backend-course:8082/
    const res = await fetch('/api/course/schedule/1001')
    if (!res.ok) {
      const body = await res.json().catch(() => ({}))
      throw new Error(body.error || `HTTP ${res.status}`)
    }
    result.value = await res.json()
  } catch (e) {
    error.value = e.message
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.container { font-family: sans-serif; max-width: 520px; margin: 60px auto; text-align: center; }
.hint   { color: #666; font-size: 14px; margin-bottom: 20px; }
button  { padding: 10px 24px; font-size: 16px; cursor: pointer; }
.result { margin-top: 20px; background: #e3f2fd; padding: 16px; border-radius: 8px; text-align: left; }
.error  { margin-top: 20px; background: #ffebee; padding: 16px; border-radius: 8px; }
.status { margin-top: 20px; color: #888; }
</style>
