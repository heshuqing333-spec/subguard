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
.selector, .guide { margin-top: 28rpx; }
.label { margin-bottom: 12rpx; color: #334155; font-size: 26rpx; font-weight: 700; }
.picker { height: 88rpx; padding: 0 24rpx; border: 1rpx solid #bfdbfe; border-radius: 16rpx; background: #f8fbff; font-size: 28rpx; line-height: 88rpx; }
.top { display: flex; justify-content: space-between; gap: 20rpx; margin-bottom: 24rpx; }
.platform { font-size: 34rpx; font-weight: 800; }
.method { margin-top: 8rpx; color: #64748b; font-size: 24rpx; }
.tag { height: 44rpx; padding: 0 16rpx; border-radius: 999rpx; background: #dbeafe; color: #1d4ed8; font-size: 24rpx; font-weight: 800; line-height: 44rpx; }
.step { display: flex; gap: 18rpx; margin-top: 18rpx; padding: 20rpx; border-radius: 16rpx; background: #f8fbff; }
.num { width: 44rpx; height: 44rpx; border-radius: 999rpx; background: #2563eb; color: #fff; text-align: center; line-height: 44rpx; font-weight: 800; }
.step-text { flex: 1; color: #0f172a; font-size: 28rpx; line-height: 1.5; }
</style>
