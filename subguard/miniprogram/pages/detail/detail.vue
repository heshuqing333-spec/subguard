<template>
  <view class="page">
    <view class="title">{{ isEdit ? '编辑订阅' : '新增订阅' }}</view>
    <view class="subtitle">记录订阅金额、扣费周期和使用价值。</view>

    <view class="card form">
      <view class="field"><text>订阅名称</text><input v-model="form.name" placeholder="例如 腾讯视频会员" /></view>
      <view class="field"><text>分类</text><picker :range="categories" :value="categoryIndex" @change="pickCategory"><view class="picker">{{ form.category }}</view></picker></view>
      <view class="field"><text>价格</text><input v-model="form.price" type="digit" placeholder="例如 30" /></view>
      <view class="field"><text>周期</text><picker :range="cycleLabels" :value="cycleIndex" @change="pickCycle"><view class="picker">{{ cycleLabels[cycleIndex] }}</view></picker></view>
      <view class="field"><text>下次扣费日期</text><picker mode="date" :value="form.next_due_date" @change="pickDate"><view class="picker">{{ form.next_due_date }}</view></picker></view>
      <view class="field"><text>支付方式</text><picker :range="payments" :value="paymentIndex" @change="pickPayment"><view class="picker">{{ form.payment_method }}</view></picker></view>
      <view class="field"><text>状态</text><picker :range="statusLabels" :value="statusIndex" @change="pickStatus"><view class="picker">{{ statusLabels[statusIndex] }}</view></picker></view>
      <view class="field"><text>本月使用次数</text><input v-model="form.usage_count" type="number" placeholder="例如 12" /></view>
      <view class="field"><text>重要程度</text><input v-model="form.importance" type="number" placeholder="1 到 5" /></view>
      <view class="field"><text>备注</text><textarea v-model="form.notes" placeholder="续费前需要注意的事" /></view>
      <button class="primary-btn" :loading="submitting" :disabled="submitting" @click="submit">{{ isEdit ? '保存修改' : '添加订阅' }}</button>
    </view>
  </view>
</template>

<script>
const api = require('../../utils/api')
const cycles = [{ label: '月付', value: 'monthly' }, { label: '年付', value: 'yearly' }, { label: '周付', value: 'weekly' }, { label: '试用', value: 'trial' }, { label: '自定义', value: 'custom' }]
const statuses = [{ label: '使用中', value: 'active' }, { label: '暂停', value: 'paused' }, { label: '已取消', value: 'cancelled' }]

function today() {
  const d = new Date()
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

export default {
  data() {
    return {
      id: '',
      isEdit: false,
      submitting: false,
      categories: ['影音娱乐', '学习', 'AI工具', '云存储', '购物', '其他'],
      payments: ['微信', '支付宝', 'Apple ID', '银行卡', '网页支付'],
      cycleLabels: cycles.map((item) => item.label),
      statusLabels: statuses.map((item) => item.label),
      categoryIndex: 5,
      cycleIndex: 0,
      paymentIndex: 0,
      statusIndex: 0,
      form: { name: '', category: '其他', price: '', cycle: 'monthly', next_due_date: today(), payment_method: '微信', status: 'active', usage_count: 0, importance: 3, notes: '' }
    }
  },
  onLoad(options) {
    this.id = options.id || ''
    this.isEdit = Boolean(this.id)
    if (this.isEdit) this.load()
  },
  methods: {
    load() {
      api.getSubscriptionById(this.id).then((data) => {
        this.form = { ...this.form, ...data, price: String(data.price || '') }
        this.categoryIndex = Math.max(0, this.categories.indexOf(this.form.category))
        this.cycleIndex = Math.max(0, cycles.findIndex((item) => item.value === this.form.cycle))
        this.paymentIndex = Math.max(0, this.payments.indexOf(this.form.payment_method))
        this.statusIndex = Math.max(0, statuses.findIndex((item) => item.value === this.form.status))
      })
    },
    pickCategory(e) { this.categoryIndex = Number(e.detail.value); this.form.category = this.categories[this.categoryIndex] },
    pickCycle(e) { this.cycleIndex = Number(e.detail.value); this.form.cycle = cycles[this.cycleIndex].value },
    pickDate(e) { this.form.next_due_date = e.detail.value },
    pickPayment(e) { this.paymentIndex = Number(e.detail.value); this.form.payment_method = this.payments[this.paymentIndex] },
    pickStatus(e) { this.statusIndex = Number(e.detail.value); this.form.status = statuses[this.statusIndex].value },
    validate() {
      if (!this.form.name.trim()) return '请输入订阅名称'
      if (this.form.price === '' || Number(this.form.price) < 0) return '请输入有效价格'
      if (!this.form.next_due_date) return '请选择下次扣费日期'
      if (Number(this.form.importance) < 1 || Number(this.form.importance) > 5) return '重要程度需为 1 到 5'
      return ''
    },
    submit() {
      const error = this.validate()
      if (error) return uni.showToast({ title: error, icon: 'none' })
      const payload = { ...this.form, price: Number(this.form.price), usage_count: Number(this.form.usage_count), importance: Number(this.form.importance) }
      this.submitting = true
      const req = this.isEdit ? api.updateSubscription(this.id, payload) : api.createSubscription(payload)
      req.then(() => {
        uni.showToast({ title: this.isEdit ? '已更新' : '已添加' })
        setTimeout(() => uni.switchTab({ url: '/pages/list/list' }), 500)
      }).catch((err) => uni.showToast({ title: err.message || '提交失败', icon: 'none' })).finally(() => { this.submitting = false })
    }
  }
}
</script>

<style>
.form { margin-top: 24rpx; }
.field { margin-bottom: 22rpx; }
.field text { display: block; margin-bottom: 10rpx; color: #334155; font-size: 24rpx; font-weight: 700; }
input, .picker, textarea { width: 100%; box-sizing: border-box; border: 1rpx solid #cbd5e1; border-radius: 14rpx; background: #f8fafc; color: #0f172a; font-size: 26rpx; }
input, .picker { height: 78rpx; padding: 0 22rpx; line-height: 78rpx; }
textarea { min-height: 160rpx; padding: 20rpx 22rpx; line-height: 1.45; }
</style>
