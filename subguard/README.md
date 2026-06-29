# SubGuard 订阅管理助手

SubGuard 是一个订阅管理助手，目标是帮助用户管理视频会员、音乐会员、AI 工具、网盘、学习平台等订阅服务。规划功能包括续费提醒、支出统计、文本账单识别、CSV 账单导入识别、取消路径提示和订阅价值评分。

当前阶段只初始化项目结构和最小可运行骨架，复杂业务逻辑后续再实现。

## 项目结构

```text
subguard/
├── miniprogram/
│   ├── app.js
│   ├── app.json
│   ├── app.wxss
│   ├── utils/
│   │   └── api.js
│   └── pages/
│       ├── index/
│       ├── list/
│       ├── detail/
│       ├── import-text/
│       ├── import-csv/
│       ├── stats/
│       └── cancel-guide/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── extensions.py
│   ├── routes/
│   ├── services/
│   ├── requirements.txt
│   └── instance/
└── README.md
```

## 运行 Flask 后端

进入后端目录：

```bash
cd subguard/backend
```

创建并激活虚拟环境：

```bash
python -m venv .venv
.venv\Scripts\activate
```

安装依赖：

```bash
pip install -r requirements.txt
```

启动服务：

```bash
python app.py
```

健康检查接口：

```text
GET http://127.0.0.1:5000/api/health
```

预期返回：

```json
{
  "service": "subguard-backend",
  "status": "ok"
}
```

## 运行微信小程序

1. 打开微信开发者工具。
2. 选择“导入项目”。
3. 项目目录选择 `subguard/miniprogram`。
4. AppID 可先选择测试号或使用自己的小程序 AppID。
5. 确认 Flask 后端已运行在 `http://127.0.0.1:5000`。
6. 在开发者工具中预览或编译运行。

小程序首页会请求 `/api/health`，用于确认后端连接状态。

## 后端 API

所有接口返回 JSON，日期统一使用 `YYYY-MM-DD` 格式。当前版本暂不实现用户登录，默认单用户使用。

### 健康检查

```text
GET /api/health
```

### 订阅管理

```text
GET /api/subscriptions
```

获取所有订阅。

```text
GET /api/subscriptions/<id>
```

获取单个订阅。订阅不存在时返回 `404`。

```text
POST /api/subscriptions
```

新增订阅。请求体示例：

```json
{
  "name": "腾讯视频会员",
  "category": "影音娱乐",
  "price": 30,
  "cycle": "monthly",
  "next_due_date": "2026-06-18",
  "payment_method": "微信",
  "status": "active",
  "usage_count": 12,
  "importance": 4,
  "notes": "续费前确认是否有优惠"
}
```

```text
PUT /api/subscriptions/<id>
```

更新订阅。请求体可传入部分字段，订阅不存在时返回 `404`。

```text
DELETE /api/subscriptions/<id>
```

删除订阅。订阅不存在时返回 `404`。

```text
GET /api/subscriptions/upcoming?days=7
```

获取未来指定天数内即将续费的 active 订阅，`days` 默认值为 `7`。

### 字段校验

`POST` 创建订阅时必须提供：

- `name`：不能为空。
- `price`：必须是大于等于 0 的数字。
- `cycle`：必须是 `monthly`、`yearly`、`weekly`、`trial`、`custom` 之一。
- `next_due_date`：必须使用 `YYYY-MM-DD` 格式。

可选字段：

- `category`：例如 `影音娱乐`、`学习`、`AI工具`、`云存储`、`购物`、`其他`。
- `payment_method`：例如 `微信`、`支付宝`、`Apple ID`、`银行卡`、`网页支付`。
- `status`：必须是 `active`、`paused`、`cancelled` 之一。
- `usage_count`：必须是大于等于 0 的整数。
- `importance`：必须是 1 到 5 的整数。
- `notes`：备注。
