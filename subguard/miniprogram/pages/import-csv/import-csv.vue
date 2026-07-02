<template>
  <view class="page">
    <view class="title">CSV 账单导入</view>
    <view class="subtitle">上传包含 date、merchant、amount、payment_method 字段的 CSV。</view>
    <view class="card upload">
      <view class="upload-title">选择账单文件</view>
      <view class="upload-desc">从微信聊天文件中选择 CSV 文件。</view>
      <button class="primary-btn" :loading="uploading" :disabled="uploading" @click="choose">{{ uploading ? '识别中...' : '选择 CSV 文件' }}</button>
      <view v-if="fileName" class="file-name">已选择：{{ fileName }}</view>
    </view>
    <view v-if="errorMessage" class="notice">{{ errorMessage }}</view>
    <view v-if="!uploading && !errorMessage && candidates.length === 0" class="empty">导入后会显示疑似订阅和识别依据。</view>
    <view v-for="(item, index) in candidates" :key="item.localId" class="card candidate">
      <view class="top"><view><view class="name">{{ item.name }}</view><view class="meta">{{ item.payment_method || '未知支付方式' }} · {{ item.cycleText }}</view></view><view class="confidence">{{ item.confidenceText }}</view></view>
      <view class="grid">
        <view class="info"><text>金额</text><view>¥{{ item.priceText }}</view></view>
        <view class="info"><text>下次扣费</text><view>{{ item.next_due_date || '未识别' }}</view></view>
      </view>
      <view class="evidence"><text>识别依据</text><view>{{ item.evidence }}</view></view>
      <button class="primary-btn" :class="{ added: item.added }" :loading="item.adding" :disabled="item.adding || item.added" @click="save(index)">{{ item.added ? '已添加' : '确认添加' }}</button>
    </view>
  </view>
</template>

<script>
const api = require('../../utils/api')
const cycleLabels = { monthly: '月付', yearly: '年付', weekly: '周付', trial: '试用', custom: '自定义' }

export default {
  data() { return { fileName: '', uploading: false, errorMessage: '', candidates: [] } },
  methods: {
    choose() {
      wx.chooseMessageFile({
        count: 1,
        type: 'file',
        extension: ['csv'],
        success: (res) => {
          const file = res.tempFiles && res.tempFiles[0]
          if (!file) return
          if (!/\.csv$/i.test(file.name)) { this.errorMessage = '请选择 CSV 格式文件。'; return }
          this.fileName = file.name
          this.upload(file.path)
        },
        fail: () => { this.errorMessage = '未选择文件。' }
      })
    },
    upload(path) {
      this.uploading = true; this.errorMessage = ''; this.candidates = []
      api.importCSV(path).then((data) => {
        const rows = data.subscriptions || []
        if (rows.length === 0) { this.errorMessage = '未识别出疑似订阅，请确认 CSV 字段和账单内容。'; return }
        this.candidates = rows.map((item, index) => ({ ...item, localId: `${item.name}-${index}`, priceText: Number(item.price || 0).toFixed(2), cycleText: cycleLabels[item.cycle] || item.cycle, confidenceText: `${Math.round(Number(item.confidence || 0) * 100)}%`, adding: false, added: false }))
      }).catch((err) => { this.errorMessage = err.message || '上传或识别失败，请检查 CSV 格式。' }).finally(() => { this.uploading = false })
    },
    save(index) {
      const item = this.candidates[index]
      if (!item || !item.next_due_date) return uni.showToast({ title: '缺少扣费日期', icon: 'none' })
      this.$set(this.candidates[index], 'adding', true)
      api.createSubscription({ name: item.name, category: '其他', price: Number(item.price || 0), cycle: item.cycle || 'monthly', next_due_date: item.next_due_date, payment_method: item.payment_method || '网页支付', status: 'active', usage_count: 0, importance: 3, notes: `CSV 导入，置信度 ${item.confidenceText}。${item.evidence || ''}` }).then(() => {
        uni.showToast({ title: '已添加' })
        this.$set(this.candidates[index], 'added', true)
      }).finally(() => { this.$set(this.candidates[index], 'adding', false) })
    }
  }
}
</script>

<style>
.upload, .candidate { margin-top: 24rpx; }
.upload-title { font-size: 30rpx; font-weight: 800; }
.upload-desc, .file-name, .meta { margin-top: 9rpx; color: #64748b; font-size: 23rpx; line-height: 1.45; }
.top { display: flex; justify-content: space-between; gap: 20rpx; }
.name { font-size: 31rpx; font-weight: 800; line-height: 1.25; }
.confidence { padding: 7rpx 14rpx; border-radius: 999rpx; background: #dbeafe; color: #1d4ed8; font-size: 23rpx; font-weight: 800; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14rpx; margin-top: 20rpx; }
.info, .evidence { padding: 16rpx; border-radius: 14rpx; background: #f8fafc; }
.info text, .evidence text { color: #64748b; font-size: 21rpx; }
.info view, .evidence view { margin-top: 7rpx; font-size: 24rpx; font-weight: 700; line-height: 1.45; }
.evidence { margin-top: 18rpx; margin-bottom: 20rpx; }
.added { background: #dcfce7; color: #047857; }
</style>
