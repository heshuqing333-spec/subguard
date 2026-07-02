<template>
  <view class="page">
    <view class="title">取消路径</view>
    <view class="subtitle">选择支付方式，查看关闭自动续费或扣费服务的入口。</view>
    <view class="card selector">
      <view class="label">支付方式</view>
      <picker :range="payments" :value="paymentIndex" @change="pick"><view class="picker">{{ selectedPayment }}</view></picker>
    </view>
    <view v-if="errorMessage" class="notice">{{ errorMessage }}</view>
    <view class="card guide">
      <view class="top"><view><view class="platform">{{ guide.platform_name }}</view><view class="method">{{ guide.payment_method }}</view></view><view class="tag">{{ matched ? '已匹配' : '通用提示' }}</view></view>
      <view v-for="(step, index) in guide.steps" :key="index" class="step"><view class="num">{{ index + 1 }}</view><view class="step-text">{{ step }}</view></view>
    </view>
  </view>
</template>

<script>
const api = require('../../utils/api')
const fallback = { payment_method: '通用', platform_name: '通用取消提示', guide_steps: '请前往对应 App 的会员中心、账户设置或支付设置中查看自动续费项目。' }
function normalize(guide) { const item = guide || fallback; return { ...item, steps: item.guide_steps.indexOf('→') >= 0 ? item.guide_steps.split('→').map((x) => x.trim()).filter(Boolean) : [item.guide_steps] } }
export default {
  data() { return { payments: ['微信', '支付宝', 'Apple ID', 'Google Play', '网页支付'], paymentIndex: 0, selectedPayment: '微信', guide: normalize(fallback), matched: false, errorMessage: '' } },
  onLoad(options) {
    const payment = decodeURIComponent(options.payment_method || '')
    const index = this.payments.indexOf(payment)
    if (index >= 0) { this.paymentIndex = index; this.selectedPayment = payment }
    this.load()
  },
  methods: {
    pick(e) { this.paymentIndex = Number(e.detail.value); this.selectedPayment = this.payments[this.paymentIndex]; this.load() },
    load() {
      this.errorMessage = ''
      api.getCancelGuide(this.selectedPayment).then((data) => {
        const guides = data.cancel_guides || []
        this.matched = guides.length > 0
        this.guide = normalize(guides[0])
      }).catch((err) => { this.errorMessage = err.message || '取消路径加载失败。'; this.matched = false; this.guide = normalize(fallback) })
    }
  }
}
</script>

<style>
.selector, .guide { margin-top: 24rpx; }
.label { margin-bottom: 10rpx; color: #334155; font-size: 24rpx; font-weight: 700; }
.picker { height: 78rpx; padding: 0 22rpx; border: 1rpx solid #cbd5e1; border-radius: 14rpx; background: #f8fafc; font-size: 26rpx; line-height: 78rpx; }
.top { display: flex; justify-content: space-between; gap: 18rpx; margin-bottom: 20rpx; }
.platform { font-size: 31rpx; font-weight: 800; line-height: 1.25; }
.method { margin-top: 7rpx; color: #64748b; font-size: 23rpx; }
.tag { height: 40rpx; padding: 0 14rpx; border-radius: 999rpx; background: #dbeafe; color: #1d4ed8; font-size: 22rpx; font-weight: 800; line-height: 40rpx; }
.step { display: flex; gap: 16rpx; margin-top: 14rpx; padding: 17rpx; border-radius: 14rpx; background: #f8fafc; }
.num { width: 40rpx; height: 40rpx; border-radius: 999rpx; background: #2563eb; color: #fff; text-align: center; line-height: 40rpx; font-size: 23rpx; font-weight: 800; }
.step-text { flex: 1; color: #0f172a; font-size: 25rpx; line-height: 1.45; }
</style>
