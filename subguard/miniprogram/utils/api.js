const BASE_URL = 'http://127.0.0.1:5000/api'

function client() {
  if (typeof uni !== 'undefined') {
    return uni
  }
  return wx
}

function buildUrl(path) {
  if (path.startsWith('http')) {
    return path
  }
  return `${BASE_URL}${path}`
}

function normalizeError(res) {
  const data = res && res.data
  if (data && data.error) {
    return data.error
  }
  if (data && data.message) {
    return data.message
  }
  return `请求失败，状态码 ${res.statusCode}`
}

function request(path, options = {}) {
  return new Promise((resolve, reject) => {
    client().request({
      url: buildUrl(path),
      method: options.method || 'GET',
      data: options.data || {},
      header: {
        'content-type': 'application/json',
        ...(options.header || {})
      },
      success(res) {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
          return
        }
        reject(new Error(normalizeError(res)))
      },
      fail(error) {
        reject(new Error(error.errMsg || '网络请求失败'))
      }
    })
  })
}

function uploadFile(path, filePath, options = {}) {
  return new Promise((resolve, reject) => {
    client().uploadFile({
      url: buildUrl(path),
      filePath,
      name: options.name || 'file',
      formData: options.formData || {},
      success(res) {
        let data = res.data
        try {
          data = data ? JSON.parse(data) : {}
        } catch (error) {
          reject(new Error('接口返回不是有效 JSON'))
          return
        }

        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(data)
          return
        }
        reject(new Error(data.error || data.message || `上传失败，状态码 ${res.statusCode}`))
      },
      fail(error) {
        reject(new Error(error.errMsg || '文件上传失败'))
      }
    })
  })
}

function healthCheck() {
  return request('/health')
}

function getSubscriptions() {
  return request('/subscriptions')
}

function getSubscriptionById(id) {
  return request(`/subscriptions/${id}`)
}

function createSubscription(data) {
  return request('/subscriptions', {
    method: 'POST',
    data
  })
}

function updateSubscription(id, data) {
  return request(`/subscriptions/${id}`, {
    method: 'PUT',
    data
  })
}

function deleteSubscription(id) {
  return request(`/subscriptions/${id}`, {
    method: 'DELETE'
  })
}

function getUpcomingSubscriptions(days = 7) {
  return request(`/subscriptions/upcoming?days=${days}`)
}

function importText(text) {
  return request('/import/text', {
    method: 'POST',
    data: { text }
  })
}

function importImage(filePath) {
  return uploadFile('/import/image', filePath)
}

function importCSV(filePath) {
  return uploadFile('/import/csv', filePath)
}

function getStatsSummary() {
  return request('/stats/summary')
}

function getCancelGuide(paymentMethod) {
  return request(`/cancel-guides?payment_method=${encodeURIComponent(paymentMethod || '')}`)
}

module.exports = {
  BASE_URL,
  request,
  uploadFile,
  healthCheck,
  health: healthCheck,
  getSubscriptions,
  getSubscriptionById,
  createSubscription,
  updateSubscription,
  deleteSubscription,
  getUpcomingSubscriptions,
  importText,
  importImage,
  importCSV,
  getStatsSummary,
  getCancelGuide
}
