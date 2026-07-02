<template>
  <view class="page">
    <view class="header">
      <view>
        <view class="title">订阅列表</view>
        <view class="subtitle">查看扣费日期、支付方式和价值评分。</view>
      </view>
      <button class="add-btn" @click="add">添加</button>
    </view>

    <view v-if="errorMessage" class="notice">{{ errorMessage }}</view>
    <view v-if="!loading && subscriptions.length === 0" class="empty">
      <view class="empty-title">还没有订阅</view>
      <view class="empty-text">添加第一个订阅后，就能看到续费提醒和价值评分。</view>
      <button class="primary-btn empty-action" @click="add">添加订阅</button>
    </view>

    <view v-for="item in subscriptions" :key="item.id" class="card sub-card" :class="item.reminderClass">
      <view v-if="item.reminderText" class="reminder" :class="'reminder-' + item.reminderClass">{{ item.reminderText }}</view>
      <view class="top">
        <view>
          <view class="name">{{ item.name }}</view>
          <view class="tag">{{ item.category }}</view>
        </view>
        <view class="status">{{ item.statusText }}</view>
      </view>
      <view class="price">¥{{ item.priceText }} <text class="cycle">/ {{ item.cycleText }}</text></view>
      <view class="grid">
        <view class="info"><text>下次扣费</text><view>{{ item.next_due_date || '未设置' }}</view></view>
        <view class="info"><text>支付方式</text><view>{{ item.payment_method || '未设置' }}</view></view>
        <view class="info"><text>本月使用</text><view>{{ item.usage_count }} 次</view></view>
        <view class="info"><text>重要程度</text><view>{{ item.importance }} / 5</view></view>
      </view>
      <view class="advice">{{ item.valueAdvice }}</view>
      <view class="actions">
        <button class="secondary-btn small" @click="edit(item.id)">编辑</button>
        <button class="secondary-btn small" @click="guide(item.payment_method)">取消路径</button>
        <button class="secondary-btn small danger" @click="remove(item)">删除</button>
      </view>
    </view>
  </view>
</template>

<script>
const api = require('../../utils/api')
const cycleLabels = { monthly: '月付', yearly: '年付', weekly: '周付', trial: '试用', custom: '自定义' }
const statusLabels = { active: '使用中', paused: '暂停', cancelled: '已取消' }

function parseDate(text) {
  if (!text) return null
  const parts = text.split('-').map(Number)
  return new Date(parts[0], parts[1] - 1, parts[2])
}

function reminder(item) {
  if (item.status !== 'active' || !item.next_due_date) return {}
  const now = new Date()
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate())
  const diff = Math.floor((parseDate(item.next_due_date) - today) / 86400000)
  if (diff < 0) return { reminderText: '可能已扣费，请确认', reminderClass: 'overdue' }
  if (diff <= 3) return { reminderText: diff === 0 ? '今天即将扣费' : `${diff} 天内即将扣费`, reminderClass: 'urgent' }
  if (diff <= 7) return { reminderText: `${diff} 天后续费`, reminderClass: 'upcoming' }
  return {}
}

export default {
  data() {
    return { loading: true, errorMessage: '', subscriptions: [] }
  },
  onLoad() { this.load() },
  onShow() { this.load() },
  onPullDownRefresh() { this.load().finally(() => uni.stopPullDownRefresh()) },
  methods: {
    load() {
      this.loading = true
      this.errorMessage = ''
      return api.getSubscriptions().then((rows) => {
        this.subscriptions = rows.map((item) => ({
          ...item,
          ...reminder(item),
          priceText: Number(item.price || 0).toFixed(2),
          cycleText: cycleLabels[item.cycle] || item.cycle,
          statusText: statusLabels[item.status] || item.status,
          valueAdvice: item.score ? `${item.score} 分，${item.suggestion}` : '建议续费前再评估一次。'
        }))
      }).catch(() => {
        this.errorMessage = '订阅列表加载失败，请确认后端服务已启动。'
      }).finally(() => { this.loading = false })
    },
    add() { uni.navigateTo({ url: '/pages/detail/detail' }) },
    edit(id) { uni.navigateTo({ url: `/pages/detail/detail?id=${id}` }) },
    guide(payment) { uni.navigateTo({ url: `/pages/cancel-guide/cancel-guide?payment_method=${encodeURIComponent(payment || '')}` }) },
    remove(item) {
      uni.showModal({
        title: '删除订阅',
        content: `确定删除「${item.name}」吗？`,
        confirmText: '删除',
        confirmColor: '#dc2626',
        success: (res) => {
          if (!res.confirm) return
          api.deleteSubscription(item.id).then(() => {
            uni.showToast({ title: '已删除' })
            this.load()
          })
        }
      })
    }
  }
}
</script>

<style>
.header { display: flex; justify-content: space-between; align-items: flex-start; gap: 20rpx; margin-bottom: 24rpx; }
.add-btn { flex: 0 0 auto; min-width: 104rpx; height: 60rpx; border-radius: 14rpx; background: #2563eb; color: #fff; font-size: 25rpx; line-height: 60rpx; }
.empty-title { color: #0f172a; font-size: 30rpx; font-weight: 800; }
.empty-text { margin-top: 10rpx; font-size: 24rpx; line-height: 1.45; }
.empty-action { width: 240rpx; margin-top: 24rpx; }
.sub-card { margin-bottom: 20rpx; }
.sub-card.upcoming { border-color: #93c5fd; }
.sub-card.urgent { border-color: #f59e0b; }
.sub-card.overdue { border-color: #fca5a5; }
.reminder { margin-bottom: 18rpx; padding: 13rpx 18rpx; border-radius: 14rpx; font-size: 24rpx; font-weight: 800; }
.reminder-upcoming { background: #dbeafe; color: #1d4ed8; }
.reminder-urgent { background: #fef3c7; color: #92400e; }
.reminder-overdue { background: #fee2e2; color: #b91c1c; }
.top { display: flex; justify-content: space-between; gap: 20rpx; }
.name { color: #0f172a; font-size: 31rpx; font-weight: 800; line-height: 1.25; }
.tag, .status { display: inline-flex; margin-top: 10rpx; padding: 5rpx 12rpx; border-radius: 999rpx; background: #eff6ff; color: #2563eb; font-size: 21rpx; font-weight: 700; }
.price { margin-top: 20rpx; color: #2563eb; font-size: 42rpx; font-weight: 800; line-height: 1.1; }
.cycle { color: #64748b; font-size: 23rpx; font-weight: 400; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14rpx; margin-top: 20rpx; }
.info { padding: 16rpx; border-radius: 14rpx; background: #f8fafc; }
.info text { color: #64748b; font-size: 21rpx; }
.info view { margin-top: 7rpx; color: #0f172a; font-size: 24rpx; font-weight: 700; }
.advice { margin-top: 18rpx; padding: 18rpx; border-radius: 14rpx; background: #eff6ff; color: #1e3a8a; font-size: 24rpx; line-height: 1.45; }
.actions { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 12rpx; margin-top: 20rpx; }
.small { height: 60rpx; font-size: 23rpx; line-height: 60rpx; border-radius: 12rpx; }
.danger { color: #dc2626; background: #fef2f2; }
</style>
