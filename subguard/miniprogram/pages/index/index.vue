<template>
  <view class="page">
    <view class="hero">
      <view class="eyebrow">SubGuard</view>
      <view class="title">订阅管理助手</view>
      <view class="subtitle">管理自动续费、账单导入、支出统计和取消路径。</view>
    </view>

    <view v-if="errorMessage" class="notice">{{ errorMessage }}</view>

    <view v-if="reminderVisible" class="card reminder-card">
      <view class="reminder-head">
        <view>
          <view class="reminder-title">即将扣费提醒</view>
          <view class="reminder-subtitle">未来 7 天有订阅即将自动扣费</view>
        </view>
      </view>
      <view class="reminder-list">
        <view v-for="item in reminderItems" :key="item.id" class="reminder-item" @click="viewUpcomingSubscription(item)">
          <text>{{ item.name }}</text>
          <text>{{ item.next_due_date }} · ¥{{ item.priceText }}</text>
        </view>
        <view v-if="reminderMoreCount > 0" class="reminder-more">
          还有 {{ reminderMoreCount }} 项即将扣费
        </view>
      </view>
      <view class="reminder-actions">
        <button class="secondary-btn reminder-btn" @click="dismissUpcomingReminder">稍后提醒</button>
        <button class="primary-btn reminder-btn" @click="viewUpcomingSubscriptions">查看最近订阅</button>
      </view>
    </view>

    <view class="stats-grid">
      <view class="card stat-card main">
        <view class="stat-label">本月订阅支出</view>
        <view class="stat-value money">¥{{ monthlyExpense }}</view>
      </view>
      <view class="card stat-card">
        <view class="stat-label">未来 7 天续费</view>
        <view class="stat-value">{{ upcomingCount }}</view>
      </view>
      <view class="card stat-card">
        <view class="stat-label">当前订阅总数</view>
        <view class="stat-value">{{ subscriptionCount }}</view>
      </view>
    </view>

    <view class="section-title">功能入口</view>
    <view class="entry-grid">
      <view v-for="item in entrances" :key="item.title" class="card entry-card" @click="go(item)">
        <view class="entry-icon">{{ item.icon }}</view>
        <view class="entry-title">{{ item.title }}</view>
        <view class="entry-desc">{{ item.desc }}</view>
      </view>
    </view>

    <view v-if="loading" class="loading">加载中...</view>
  </view>
</template>

<script>
const api = require('../../utils/api')

function money(value) {
  return Number(value || 0).toFixed(2)
}

export default {
  data() {
    return {
      loading: true,
      errorMessage: '',
      monthlyExpense: '0.00',
      upcomingCount: 0,
      subscriptionCount: 0,
      reminderVisible: false,
      reminderItems: [],
      reminderMoreCount: 0,
      entrances: [
        { icon: '订', title: '订阅列表', desc: '查看全部订阅', url: '/pages/list/list', type: 'switchTab' },
        { icon: '+', title: '添加订阅', desc: '记录新的扣费项', url: '/pages/detail/detail' },
        { icon: '文', title: '文本识别', desc: '粘贴账单自动识别', url: '/pages/import-text/import-text' },
        { icon: 'CSV', title: 'CSV 导入', desc: '批量导入账单', url: '/pages/import-csv/import-csv' },
        { icon: '统', title: '支出统计', desc: '查看月度趋势', url: '/pages/stats/stats', type: 'switchTab' },
        { icon: '关', title: '取消路径', desc: '查找关闭入口', url: '/pages/cancel-guide/cancel-guide' }
      ]
    }
  },
  onLoad() {
    this.load()
  },
  onPullDownRefresh() {
    this.load().finally(() => uni.stopPullDownRefresh())
  },
  methods: {
    load() {
      this.loading = true
      this.errorMessage = ''
      return Promise.all([
        api.getSubscriptions(),
        api.getUpcomingSubscriptions(7),
        api.getStatsSummary().catch(() => null)
      ]).then(([subscriptions, upcoming, stats]) => {
        const active = subscriptions.filter((item) => item.status !== 'cancelled')
        this.monthlyExpense = money(stats ? stats.total_monthly_cost : 0)
        this.upcomingCount = stats ? stats.upcoming_count : upcoming.length
        this.subscriptionCount = stats ? stats.subscription_count : active.length
        this.prepareUpcomingReminder(upcoming)
      }).catch(() => {
        this.errorMessage = '暂时无法连接后端，请确认 Flask 服务已启动。'
      }).finally(() => {
        this.loading = false
      })
    },
    todayReminderKey() {
      const today = new Date()
      const todayText = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`
      return `subguard-reminder-${todayText}`
    },
    prepareUpcomingReminder(upcoming) {
      if (!Array.isArray(upcoming) || upcoming.length === 0 || uni.getStorageSync(this.todayReminderKey())) {
        this.reminderVisible = false
        this.reminderItems = []
        this.reminderMoreCount = 0
        return
      }

      this.reminderItems = upcoming.slice(0, 3).map((item) => ({
        ...item,
        priceText: Number(item.price || 0).toFixed(2)
      }))
      this.reminderMoreCount = Math.max(0, upcoming.length - this.reminderItems.length)
      this.reminderVisible = true
    },
    dismissUpcomingReminder() {
      uni.setStorageSync(this.todayReminderKey(), '1')
      this.reminderVisible = false
    },
    viewUpcomingSubscriptions() {
      const firstItem = this.reminderItems[0]
      if (!firstItem) return
      this.viewUpcomingSubscription(firstItem)
    },
    viewUpcomingSubscription(item) {
      if (!item || !item.id) return
      uni.setStorageSync(this.todayReminderKey(), '1')
      this.reminderVisible = false
      uni.navigateTo({ url: `/pages/detail/detail?id=${item.id}` })
    },
    go(item) {
      if (item.type === 'switchTab') {
        uni.switchTab({ url: item.url })
      } else {
        uni.navigateTo({ url: item.url })
      }
    }
  }
}
</script>

<style>
.hero { padding: 26rpx 0 24rpx; }
.eyebrow { display: inline-flex; height: 38rpx; padding: 0 16rpx; border-radius: 999rpx; background: #e0f2fe; color: #0369a1; font-size: 21rpx; font-weight: 800; line-height: 38rpx; }
.stats-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18rpx; }
.stat-card { min-height: 138rpx; }
.stat-card.main { grid-column: span 2; }
.stat-label { color: #64748b; font-size: 23rpx; }
.stat-value { margin-top: 16rpx; color: #0f172a; font-size: 44rpx; font-weight: 800; line-height: 1.1; }
.money { color: #2563eb; }
.reminder-card { margin-bottom: 22rpx; border-color: #fcd34d; background: #fffbeb; box-shadow: 0 8rpx 24rpx rgba(217, 119, 6, 0.08); }
.reminder-head { display: flex; justify-content: space-between; gap: 20rpx; }
.reminder-title { color: #92400e; font-size: 28rpx; font-weight: 800; }
.reminder-subtitle { margin-top: 6rpx; color: #b45309; font-size: 23rpx; }
.reminder-list { margin-top: 18rpx; }
.reminder-item { display: flex; justify-content: space-between; gap: 18rpx; padding: 13rpx 0; border-top: 1rpx solid #fde68a; color: #78350f; font-size: 23rpx; line-height: 1.4; }
.reminder-item text:first-child { flex: 1; min-width: 0; }
.reminder-item text:last-child { flex: 0 0 auto; color: #92400e; font-weight: 700; }
.reminder-more { padding-top: 10rpx; color: #b45309; font-size: 23rpx; }
.reminder-actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 14rpx; margin-top: 18rpx; }
.reminder-btn { height: 66rpx; border-radius: 12rpx; font-size: 24rpx; line-height: 66rpx; }
.section-title { margin: 36rpx 0 18rpx; color: #0f172a; font-size: 30rpx; font-weight: 800; }
.entry-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18rpx; }
.entry-card { min-height: 154rpx; box-sizing: border-box; }
.entry-icon { display: inline-flex; align-items: center; justify-content: center; width: 52rpx; height: 52rpx; border-radius: 14rpx; background: #eff6ff; color: #2563eb; font-size: 22rpx; font-weight: 800; }
.entry-title { margin-top: 14rpx; color: #0f172a; font-size: 28rpx; font-weight: 800; }
.entry-desc { margin-top: 8rpx; color: #64748b; font-size: 23rpx; line-height: 1.35; }
.loading { padding: 28rpx 0; color: #64748b; font-size: 24rpx; text-align: center; }
</style>
