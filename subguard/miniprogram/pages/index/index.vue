<template>
  <view class="page">
    <view class="hero">
      <view class="eyebrow">SubGuard</view>
      <view class="title">订阅管理助手</view>
      <view class="subtitle">管理自动续费、账单导入、支出统计和取消路径。</view>
    </view>

    <view v-if="errorMessage" class="notice">{{ errorMessage }}</view>

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
      entrances: [
        { icon: 'List', title: '订阅列表', desc: '查看全部订阅', url: '/pages/list/list', type: 'switchTab' },
        { icon: 'Add', title: '添加订阅', desc: '记录新的扣费项', url: '/pages/detail/detail' },
        { icon: 'Text', title: '文本识别', desc: '粘贴账单自动识别', url: '/pages/import-text/import-text' },
        { icon: 'CSV', title: 'CSV 导入', desc: '批量导入账单', url: '/pages/import-csv/import-csv' },
        { icon: 'Cost', title: '支出统计', desc: '查看月度趋势', url: '/pages/stats/stats', type: 'switchTab' },
        { icon: 'Off', title: '取消路径', desc: '查找关闭入口', url: '/pages/cancel-guide/cancel-guide' }
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
      }).catch(() => {
        this.errorMessage = '暂时无法连接后端，请确认 Flask 服务已启动。'
      }).finally(() => {
        this.loading = false
      })
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
.hero { padding: 36rpx 0 30rpx; }
.eyebrow { display: inline-flex; height: 40rpx; padding: 0 18rpx; border-radius: 999rpx; background: #dbeafe; color: #1d4ed8; font-size: 22rpx; font-weight: 700; line-height: 40rpx; }
.stats-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20rpx; }
.stat-card { min-height: 160rpx; }
.stat-card.main { grid-column: span 2; }
.stat-label { color: #64748b; font-size: 24rpx; }
.stat-value { margin-top: 20rpx; color: #0f172a; font-size: 50rpx; font-weight: 800; }
.money { color: #2563eb; }
.section-title { margin: 42rpx 0 20rpx; color: #0f172a; font-size: 32rpx; font-weight: 800; }
.entry-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 20rpx; }
.entry-card { min-height: 176rpx; box-sizing: border-box; }
.entry-icon { display: inline-flex; align-items: center; justify-content: center; min-width: 58rpx; height: 58rpx; padding: 0 12rpx; border-radius: 16rpx; background: #eff6ff; color: #2563eb; font-size: 22rpx; font-weight: 800; }
.entry-title { margin-top: 18rpx; color: #0f172a; font-size: 30rpx; font-weight: 800; }
.entry-desc { margin-top: 10rpx; color: #64748b; font-size: 24rpx; line-height: 1.4; }
.loading { padding: 32rpx 0; color: #64748b; font-size: 26rpx; text-align: center; }
</style>
