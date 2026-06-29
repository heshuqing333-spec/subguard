<template>
  <view class="page">
    <view class="title">账单识别</view>
    <view class="subtitle">支持粘贴文本或上传截图，识别后可编辑信息再添加。</view>

    <view class="tabs">
      <view class="tab" :class="{ active: mode === 'text' }" @click="switchMode('text')">文本识别</view>
      <view class="tab" :class="{ active: mode === 'image' }" @click="switchMode('image')">截图识别</view>
    </view>

    <view v-if="mode === 'text'" class="card input-card">
      <textarea
        v-model="text"
        :disabled="loading"
        placeholder="例如：您已成功开通腾讯视频VIP连续包月，金额25元，将于2026-07-12自动续费。"
      />
      <view class="buttons">
        <button class="secondary-btn" :disabled="loading" @click="clear">清空</button>
        <button class="primary-btn" :disabled="loading" @click="recognizeText">
          {{ loading ? '识别中...' : '开始识别' }}
        </button>
      </view>
    </view>

    <view v-if="mode === 'image'" class="card input-card">
      <view class="upload-title">上传账单截图</view>
      <view class="upload-desc">建议上传包含商户、金额、续费日期的清晰截图。</view>
      <button class="primary-btn" :disabled="loading" @click="chooseImage">
        {{ loading ? '识别中...' : '选择图片并识别' }}
      </button>
      <view v-if="imageName" class="file-name">已选择：{{ imageName }}</view>
    </view>

    <view v-if="loading" class="card progress-card">
      <view class="spinner"></view>
      <view class="progress-title">正在识别账单</view>
      <view class="progress-text">图片 OCR 可能需要几秒，请保持当前页面打开。</view>
    </view>

    <view v-if="errorMessage && !loading" class="notice">{{ errorMessage }}</view>

    <view v-if="!result && !errorMessage && !loading" class="empty">
      识别结果会显示为可编辑表单。你可以修正名称、金额、日期和支付方式后再保存。
    </view>

    <view v-if="result && !loading" class="card result-card">
      <view class="result-head">
        <view>
          <view class="result-title">识别结果</view>
          <view class="result-subtitle">请确认并编辑后添加到订阅列表。</view>
        </view>
        <view class="confidence">{{ result.confidenceText }}</view>
      </view>

      <view class="field">
        <text>订阅名称</text>
        <input v-model="result.name" placeholder="订阅名称" />
      </view>
      <view class="field">
        <text>金额</text>
        <input v-model="result.price" type="digit" placeholder="金额" />
      </view>
      <view class="field">
        <text>下次扣费日期</text>
        <picker mode="date" :value="result.next_due_date" @change="pickDate">
          <view class="picker">{{ result.next_due_date || '请选择日期' }}</view>
        </picker>
      </view>
      <view class="field">
        <text>支付方式</text>
        <picker :range="paymentOptions" :value="paymentIndex" @change="pickPayment">
          <view class="picker">{{ result.payment_method || '请选择支付方式' }}</view>
        </picker>
      </view>
      <view class="field">
        <text>周期</text>
        <picker :range="cycleLabels" :value="cycleIndex" @change="pickCycle">
          <view class="picker">{{ cycleLabels[cycleIndex] }}</view>
        </picker>
      </view>
      <view class="field">
        <text>分类</text>
        <picker :range="categoryOptions" :value="categoryIndex" @change="pickCategory">
          <view class="picker">{{ result.category }}</view>
        </picker>
      </view>
      <view class="field">
        <text>备注</text>
        <textarea class="notes" v-model="result.notes" placeholder="可补充识别来源或人工备注" />
      </view>

      <view v-if="rawText" class="raw-text">
        <view class="raw-title">OCR 原文</view>
        <view class="raw-content">{{ rawText }}</view>
      </view>

      <button class="primary-btn" :disabled="saving" @click="save">
        {{ saving ? '添加中...' : '确认添加' }}
      </button>
    </view>
  </view>
</template>

<script>
const api = require('../../utils/api')

const cycleOptions = [
  { label: '月付', value: 'monthly' },
  { label: '年付', value: 'yearly' },
  { label: '周付', value: 'weekly' },
  { label: '试用', value: 'trial' },
  { label: '自定义', value: 'custom' }
]

export default {
  data() {
    return {
      mode: 'text',
      text: '',
      imageName: '',
      loading: false,
      saving: false,
      errorMessage: '',
      rawText: '',
      result: null,
      paymentOptions: ['微信', '支付宝', 'Apple ID', '银行卡', '网页支付'],
      categoryOptions: ['影音娱乐', '学习', 'AI工具', '云存储', '购物', '其他'],
      cycleLabels: cycleOptions.map((item) => item.label),
      paymentIndex: 4,
      categoryIndex: 5,
      cycleIndex: 0
    }
  },
  methods: {
    switchMode(mode) {
      if (this.loading) return
      this.mode = mode
    },
    normalize(item, source) {
      const cycleIndex = Math.max(0, cycleOptions.findIndex((option) => option.value === item.cycle))
      const defaultPayment = item.payment_method || '网页支付'
      const paymentIndex = Math.max(0, this.paymentOptions.indexOf(defaultPayment))
      const confidence = Number(item.confidence || 0)

      this.cycleIndex = cycleIndex
      this.paymentIndex = paymentIndex
      this.categoryIndex = 5

      return {
        name: item.name || '',
        price: item.price === null || item.price === undefined ? '' : String(item.price),
        next_due_date: item.next_due_date || '',
        payment_method: this.paymentOptions[paymentIndex],
        cycle: item.cycle || cycleOptions[cycleIndex].value,
        category: '其他',
        confidence,
        confidenceText: `${Math.round(confidence * 100)}%`,
        notes: `${source}识别添加，置信度 ${Math.round(confidence * 100)}%`
      }
    },
    startLoading() {
      this.loading = true
      this.errorMessage = ''
      this.result = null
      this.rawText = ''
    },
    recognizeText() {
      if (!this.text.trim()) {
        this.errorMessage = '请先粘贴账单文本。'
        return
      }
      this.startLoading()
      api.importText(this.text.trim())
        .then((data) => {
          this.result = this.normalize(data.subscription, '文本')
        })
        .catch((error) => {
          this.errorMessage = error.message || '识别失败，请换一段文本再试。'
        })
        .finally(() => {
          this.loading = false
        })
    },
    chooseImage() {
      if (this.loading) return
      uni.chooseImage({
        count: 1,
        sizeType: ['compressed', 'original'],
        sourceType: ['album', 'camera'],
        success: (res) => {
          const path = res.tempFilePaths[0]
          this.imageName = path.split('/').pop() || '账单截图'
          this.uploadImage(path)
        }
      })
    },
    uploadImage(path) {
      this.startLoading()
      api.importImage(path)
        .then((data) => {
          this.rawText = data.raw_text || ''
          this.result = this.normalize(data.subscription, '截图')
        })
        .catch((error) => {
          this.errorMessage = error.message || '图片识别失败，请换一张清晰截图再试。'
        })
        .finally(() => {
          this.loading = false
        })
    },
    pickDate(event) {
      this.result.next_due_date = event.detail.value
    },
    pickPayment(event) {
      this.paymentIndex = Number(event.detail.value)
      this.result.payment_method = this.paymentOptions[this.paymentIndex]
    },
    pickCycle(event) {
      this.cycleIndex = Number(event.detail.value)
      this.result.cycle = cycleOptions[this.cycleIndex].value
    },
    pickCategory(event) {
      this.categoryIndex = Number(event.detail.value)
      this.result.category = this.categoryOptions[this.categoryIndex]
    },
    validate() {
      if (!this.result || !this.result.name.trim()) return '请输入订阅名称'
      if (this.result.price === '' || Number(this.result.price) < 0) return '请输入有效金额'
      if (!this.result.next_due_date) return '请选择下次扣费日期'
      return ''
    },
    save() {
      const error = this.validate()
      if (error) {
        uni.showToast({ title: error, icon: 'none' })
        return
      }
      this.saving = true
      api.createSubscription({
        name: this.result.name.trim(),
        category: this.result.category,
        price: Number(this.result.price),
        cycle: this.result.cycle,
        next_due_date: this.result.next_due_date,
        payment_method: this.result.payment_method,
        status: 'active',
        usage_count: 0,
        importance: 3,
        notes: this.result.notes
      }).then(() => {
        uni.showToast({ title: '已添加' })
        setTimeout(() => uni.switchTab({ url: '/pages/list/list' }), 500)
      }).catch((error) => {
        uni.showToast({ title: error.message || '添加失败', icon: 'none' })
      }).finally(() => {
        this.saving = false
      })
    },
    clear() {
      if (this.loading) return
      this.text = ''
      this.imageName = ''
      this.rawText = ''
      this.result = null
      this.errorMessage = ''
    }
  }
}
</script>

<style>
.tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16rpx;
  margin-top: 28rpx;
}

.tab {
  height: 72rpx;
  border-radius: 16rpx;
  background: #ffffff;
  color: #64748b;
  text-align: center;
  line-height: 72rpx;
  font-size: 26rpx;
  font-weight: 700;
}

.tab.active {
  background: #2563eb;
  color: #ffffff;
}

.input-card,
.result-card,
.progress-card {
  margin-top: 20rpx;
}

textarea {
  width: 100%;
  min-height: 240rpx;
  padding: 22rpx 24rpx;
  box-sizing: border-box;
  border: 1rpx solid #bfdbfe;
  border-radius: 16rpx;
  background: #f8fbff;
  font-size: 28rpx;
  line-height: 1.5;
}

.buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 18rpx;
  margin-top: 22rpx;
}

.upload-title {
  color: #0f172a;
  font-size: 32rpx;
  font-weight: 800;
}

.upload-desc,
.file-name {
  margin: 12rpx 0 22rpx;
  color: #64748b;
  font-size: 25rpx;
  line-height: 1.5;
}

.progress-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding-top: 36rpx;
  padding-bottom: 36rpx;
}

.spinner {
  width: 44rpx;
  height: 44rpx;
  border: 6rpx solid #dbeafe;
  border-top-color: #2563eb;
  border-radius: 999rpx;
  animation: spin 0.9s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-title {
  margin-top: 18rpx;
  color: #0f172a;
  font-size: 30rpx;
  font-weight: 800;
}

.progress-text {
  margin-top: 10rpx;
  color: #64748b;
  font-size: 24rpx;
  line-height: 1.5;
  text-align: center;
}

.result-head {
  display: flex;
  justify-content: space-between;
  gap: 20rpx;
  margin-bottom: 24rpx;
}

.result-title {
  font-size: 34rpx;
  font-weight: 800;
}

.result-subtitle {
  margin-top: 8rpx;
  color: #64748b;
  font-size: 24rpx;
}

.confidence {
  height: 44rpx;
  padding: 0 16rpx;
  border-radius: 999rpx;
  background: #dbeafe;
  color: #1d4ed8;
  font-weight: 800;
  line-height: 44rpx;
}

.field {
  margin-bottom: 24rpx;
}

.field text {
  display: block;
  margin-bottom: 12rpx;
  color: #334155;
  font-size: 26rpx;
  font-weight: 700;
}

input,
.picker,
.notes {
  width: 100%;
  box-sizing: border-box;
  border: 1rpx solid #bfdbfe;
  border-radius: 16rpx;
  background: #f8fbff;
  color: #0f172a;
  font-size: 28rpx;
}

input,
.picker {
  height: 84rpx;
  padding: 0 24rpx;
  line-height: 84rpx;
}

.notes {
  min-height: 140rpx;
  padding: 20rpx 24rpx;
}

.raw-text {
  margin-bottom: 24rpx;
  padding: 20rpx;
  border-radius: 16rpx;
  background: #f8fbff;
}

.raw-title {
  color: #64748b;
  font-size: 23rpx;
  font-weight: 700;
}

.raw-content {
  margin-top: 8rpx;
  color: #334155;
  font-size: 24rpx;
  line-height: 1.5;
}
</style>
