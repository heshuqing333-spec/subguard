<template>
  <view class="page">
    <view class="title">支出统计</view>
    <view class="subtitle">查看订阅的月度预算、年度预算和主要花费来源。</view>
    <view v-if="errorMessage" class="notice">{{ errorMessage }}</view>
    <view class="summary">
      <view class="card stat main"><text>本月预计支出</text><view>¥{{ totalMonthlyCost }}</view></view>
      <view class="card stat"><text>年度预计支出</text><view>¥{{ totalYearlyCost }}</view></view>
      <view class="card stat"><text>订阅总数</text><view>{{ subscriptionCount }}</view></view>
      <view class="card stat"><text>即将续费</text><view>{{ upcomingCount }}</view></view>
    </view>
    <view class="section-title">分类支出</view>
    <view v-if="categoryStats.length === 0 && !loading" class="empty">暂无分类支出数据</view>
    <view v-for="item in categoryStats" :key="item.name" class="card row">
      <view class="row-head"><text>{{ item.name }}</text><view>¥{{ item.monthlyCostText }} / 月</view></view>
      <view class="row-meta">{{ item.count }} 项 · 年度 ¥{{ item.yearlyCostText }}</view>
      <view class="bar"><view class="fill" :style="{ width: item.percent + '%' }"></view></view>
    </view>

    <view class="section-title">支付方式支出</view>
    <view v-if="paymentMethodStats.length === 0 && !loading" class="empty">暂无支付方式数据</view>
    <view v-for="item in paymentMethodStats" :key="item.name" class="card row">
      <view class="row-head"><text>{{ item.name }}</text><view>¥{{ item.monthlyCostText }} / 月</view></view>
      <view class="row-meta">{{ item.count }} 项 · 年度 ¥{{ item.yearlyCostText }}</view>
      <view class="bar"><view class="fill" :style="{ width: item.percent + '%' }"></view></view>
    </view>
    <view class="section-title">最贵订阅 Top 5</view>
    <view v-if="topExpensive.length === 0 && !loading" class="empty">暂无订阅数据</view>
    <view v-for="item in topExpensive" :key="item.id" class="card top-row">
      <view class="rank">{{ item.rank }}</view>
      <view class="body"><view class="top-name">{{ item.name }}</view><view class="meta">{{ item.category }} · {{ item.payment_method }}</view></view>
      <view class="cost">¥{{ item.monthlyCostText }}<text>年 ¥{{ item.yearlyCostText }}</text></view>
    </view>
  </view>
</template>

<script>
const api = require('../../utils/api')
function money(v) { return Number(v || 0).toFixed(2) }
export default {
  data() { return { loading: true, errorMessage: '', totalMonthlyCost: '0.00', totalYearlyCost: '0.00', subscriptionCount: 0, upcomingCount: 0, categoryStats: [], paymentMethodStats: [], topExpensive: [] } },
  onLoad() { this.load() },
  onShow() { this.load() },
  onPullDownRefresh() { this.load().finally(() => uni.stopPullDownRefresh()) },
  methods: {
    group(items, total) { return (items || []).map((item) => ({ ...item, monthlyCostText: money(item.monthly_cost), yearlyCostText: money(item.yearly_cost), percent: total ? Math.round(Number(item.monthly_cost || 0) / total * 100) : 0 })) },
    load() {
      this.loading = true; this.errorMessage = ''
      return api.getStatsSummary().then((data) => {
        const total = Number(data.total_monthly_cost || 0)
        this.totalMonthlyCost = money(total); this.totalYearlyCost = money(data.total_yearly_cost); this.subscriptionCount = data.subscription_count || 0; this.upcomingCount = data.upcoming_count || 0
        this.categoryStats = this.group(data.category_stats, total); this.paymentMethodStats = this.group(data.payment_method_stats, total)
        this.topExpensive = (data.top_expensive || []).map((item, index) => ({ ...item, rank: index + 1, monthlyCostText: money(item.monthly_cost), yearlyCostText: money(item.yearly_cost) }))
      }).catch((err) => { this.errorMessage = err.message || '统计数据加载失败。' }).finally(() => { this.loading = false })
    }
  }
}
</script>

<style>
.summary { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 18rpx; margin-top: 24rpx; }
.stat.main { grid-column: span 2; }
.stat text { color: #64748b; font-size: 23rpx; }
.stat view { margin-top: 15rpx; color: #2563eb; font-size: 38rpx; font-weight: 800; line-height: 1.1; }
.stat.main view { font-size: 48rpx; }
.section-title { margin: 32rpx 0 16rpx; font-size: 30rpx; font-weight: 800; }
.row { margin-bottom: 16rpx; }
.row-head { display: flex; justify-content: space-between; gap: 18rpx; font-size: 26rpx; font-weight: 800; }
.row-head view { color: #2563eb; }
.row-meta { margin-top: 9rpx; color: #64748b; font-size: 22rpx; }
.bar { height: 12rpx; margin-top: 16rpx; border-radius: 999rpx; background: #dbeafe; overflow: hidden; }
.fill { height: 100%; border-radius: 999rpx; background: #2563eb; }
.top-row { display: flex; align-items: center; gap: 18rpx; margin-bottom: 16rpx; }
.rank { width: 48rpx; height: 48rpx; border-radius: 999rpx; background: #2563eb; color: #fff; text-align: center; line-height: 48rpx; font-weight: 800; }
.body { flex: 1; min-width: 0; }
.top-name { font-size: 26rpx; font-weight: 800; }
.meta, .cost text { display: block; margin-top: 7rpx; color: #64748b; font-size: 22rpx; }
.cost { color: #2563eb; font-size: 26rpx; font-weight: 800; text-align: right; }
</style>
