# 智慧园区综合管理平台 · API 接口定义文档

> 本文档为全组共享的接口契约，骨架冻结后各组按此开发前端和后端。
> 技术栈：FastAPI + SQLAlchemy 2.0 + Pydantic v2，Swagger 自动生成接口文档。

---

## 一、通用约定

### 1.1 统一响应格式

```json
{
  "code": 0,
  "msg": "success",
  "data": { ... }
}
```

| 字段 | 类型 | 说明 |
|---|---|---|
| code | int | 0 表示成功，非 0 表示失败 |
| msg | string | 提示信息 |
| data | any | 业务数据，失败时为 null |

### 1.2 分页响应

列表接口统一使用以下分页结构：

```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "items": [ ... ],
    "total": 120,
    "page": 1,
    "page_size": 20
  }
}
```

分页请求参数：

| 参数 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| page | int | 1 | 页码 |
| page_size | int | 20 | 每页条数，最大 100 |

### 1.3 鉴权方式

- 登录接口返回双 Token：`access_token`（有效期 2 小时）+ `refresh_token`（有效期 7 天）
- 后续请求头携带：`Authorization: Bearer {access_token}`
- Token 过期后用 `refresh_token` 调 `POST /api/v1/auth/refresh` 获取新 Token

### 1.4 错误码分段

| 段 | 模块 | 示例 |
|---|---|---|
| 0 | 成功 | — |
| 10000-10999 | 通用错误 | 10001 参数校验失败、10002 未授权、10003 无权限 |
| 11000-11999 | 认证授权 | 11001 用户名或密码错误、11002 Token 已过期 |
| 12000-12999 | 系统管理 | 12001 用户不存在、12002 角色已存在 |
| 20000-20999 | 办公协同 | 20001 公告不存在 |
| 21000-21999 | 车辆管理 | 21001 车辆不存在、21002 车位已满 |
| 22000-22999 | 通行安防 | 22001 人脸特征提取失败、22002 未授权通行 |
| 23000-23999 | 访客管理 | 23001 访客预约不存在 |
| 24000-24999 | 设备物联 | 24001 设备不存在、24002 设备离线 |
| 25000-25999 | 事件中心 | 25001 告警不存在 |
| 26000-26999 | 报修工单 | 26001 工单不存在 |
| 30000-30999 | AI 服务 | 30001 模型推理超时、30002 向量检索失败 |

### 1.5 接口前缀

- 业务后端：`/api/v1/{模块}`
- AI 服务（内部）：`http://ai-service:8001/api/v1/{能力}`

---

## 二、认证授权模块 `/api/v1/auth`

| 方法 | 路径 | 说明 | 鉴权 |
|---|---|---|---|
| POST | `/api/v1/auth/login` | 用户名密码登录 | 否 |
| POST | `/api/v1/auth/refresh` | 刷新 Token | 否 |
| POST | `/api/v1/auth/logout` | 退出登录 | 是 |
| GET | `/api/v1/auth/me` | 获取当前登录用户信息 | 是 |
| POST | `/api/v1/auth/captcha` | 获取图形验证码 | 否 |

### POST /login 请求体

```json
{
  "username": "admin",
  "password": "xxx",
  "captcha_id": "uuid",
  "captcha_code": "1234"
}
```

### POST /login 响应 data

```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "nickname": "超级管理员",
    "avatar": "/uploads/avatar.png",
    "roles": ["admin"]
  }
}
```

---

## 三、系统管理模块 `/api/v1/system`

### 3.1 用户管理 `/users`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/system/users` | 用户列表（支持 username/dept_id/status 筛选） |
| GET | `/api/v1/system/users/{id}` | 用户详情 |
| POST | `/api/v1/system/users` | 新增用户 |
| PUT | `/api/v1/system/users/{id}` | 修改用户 |
| DELETE | `/api/v1/system/users/{id}` | 删除用户 |
| PUT | `/api/v1/system/users/{id}/password` | 重置密码 |
| PUT | `/api/v1/system/users/{id}/status` | 启用/禁用 |

**新增用户请求体：**

```json
{
  "username": "zhangsan",
  "password": "123456",
  "nickname": "张三",
  "phone": "13800138000",
  "email": "zhangsan@example.com",
  "dept_id": 3,
  "role_ids": [2, 5],
  "status": 1
}
```

### 3.2 角色管理 `/roles`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/system/roles` | 角色列表 |
| GET | `/api/v1/system/roles/{id}` | 角色详情（含菜单权限） |
| POST | `/api/v1/system/roles` | 新增角色 |
| PUT | `/api/v1/system/roles/{id}` | 修改角色 |
| DELETE | `/api/v1/system/roles/{id}` | 删除角色 |
| PUT | `/api/v1/system/roles/{id}/menus` | 分配菜单权限 |

**分配菜单权限请求体：** `{ "menu_ids": [1, 2, 3] }`

### 3.3 菜单管理 `/menus`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/system/menus` | 菜单树 |
| GET | `/api/v1/system/menus/{id}` | 菜单详情 |
| POST | `/api/v1/system/menus` | 新增菜单 |
| PUT | `/api/v1/system/menus/{id}` | 修改菜单 |
| DELETE | `/api/v1/system/menus/{id}` | 删除菜单 |

**菜单对象：**

```json
{
  "id": 1,
  "parent_id": 0,
  "name": "系统管理",
  "path": "/system",
  "component": "Layout",
  "icon": "setting",
  "sort": 1,
  "type": 1,
  "permission": "system:user:list",
  "children": []
}
```

### 3.4 部门组织 `/depts`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/system/depts` | 部门树 |
| POST | `/api/v1/system/depts` | 新增部门 |
| PUT | `/api/v1/system/depts/{id}` | 修改部门 |
| DELETE | `/api/v1/system/depts/{id}` | 删除部门 |

### 3.5 数据字典 `/dicts`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/system/dicts` | 字典类型列表 |
| POST | `/api/v1/system/dicts` | 新增字典类型 |
| PUT | `/api/v1/system/dicts/{id}` | 修改字典类型 |
| DELETE | `/api/v1/system/dicts/{id}` | 删除字典类型 |
| GET | `/api/v1/system/dicts/{type_code}/items` | 字典项列表 |
| POST | `/api/v1/system/dicts/{type_code}/items` | 新增字典项 |
| PUT | `/api/v1/system/dicts/items/{id}` | 修改字典项 |
| DELETE | `/api/v1/system/dicts/items/{id}` | 删除字典项 |

### 3.6 操作日志 `/logs`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/system/logs` | 操作日志列表（支持 username/module/时间筛选） |
| DELETE | `/api/v1/system/logs` | 清空日志 |

### 3.7 消息通知 `/messages`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/system/messages` | 我的消息列表 |
| GET | `/api/v1/system/messages/unread-count` | 未读消息数 |
| PUT | `/api/v1/system/messages/{id}/read` | 标记已读 |
| PUT | `/api/v1/system/messages/read-all` | 全部已读 |
| POST | `/api/v1/system/messages` | 发送消息（站内信） |

**发送消息请求体：**

```json
{
  "user_ids": [1, 2, 3],
  "title": "新工单待处理",
  "content": "您有一条新的告警工单待处置",
  "type": "system"
}
```

---

## 四、办公协同模块 `/api/v1/oa`

### 4.1 通知公告 `/notices`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/oa/notices` | 公告列表 |
| GET | `/api/v1/oa/notices/{id}` | 公告详情 |
| POST | `/api/v1/oa/notices` | 发布公告 |
| PUT | `/api/v1/oa/notices/{id}` | 修改公告 |
| DELETE | `/api/v1/oa/notices/{id}` | 删除公告 |

**公告对象：**

```json
{
  "title": "国庆放假通知",
  "content": "<p>...</p>",
  "type": "notice",
  "status": 1,
  "publish_time": "2026-09-08 10:00:00"
}
```

### 4.2 审批流程 `/approvals`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/oa/approval-templates` | 审批模板列表 |
| POST | `/api/v1/oa/approval-templates` | 新建审批模板 |
| PUT | `/api/v1/oa/approval-templates/{id}` | 修改模板 |
| GET | `/api/v1/oa/approvals` | 我的申请列表 |
| POST | `/api/v1/oa/approvals` | 发起审批申请 |
| GET | `/api/v1/oa/approvals/{id}` | 审批详情 |
| GET | `/api/v1/oa/approvals/todo` | 待我审批列表 |
| POST | `/api/v1/oa/approvals/{id}/approve` | 审批通过 |
| POST | `/api/v1/oa/approvals/{id}/reject` | 审批驳回 |

**发起审批请求体：**

```json
{
  "template_id": 1,
  "title": "张三的请假申请",
  "form_data": {
    "start_date": "2026-09-10",
    "end_date": "2026-09-12",
    "reason": "家中有事"
  }
}
```

### 4.3 会议室预约 `/meeting-rooms`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/oa/meeting-rooms` | 会议室列表 |
| POST | `/api/v1/oa/meeting-rooms` | 新增会议室 |
| PUT | `/api/v1/oa/meeting-rooms/{id}` | 修改会议室 |
| DELETE | `/api/v1/oa/meeting-rooms/{id}` | 删除会议室 |
| GET | `/api/v1/oa/meeting-rooms/{id}/bookings` | 某会议室预约记录 |
| GET | `/api/v1/oa/bookings` | 预约列表（按日期/会议室筛选） |
| POST | `/api/v1/oa/bookings` | 预约会议室 |
| DELETE | `/api/v1/oa/bookings/{id}` | 取消预约 |

**预约请求体：**

```json
{
  "room_id": 1,
  "start_time": "2026-09-09 14:00:00",
  "end_time": "2026-09-09 16:00:00",
  "topic": "周会",
  "attendees": [2, 3]
}
```

---

## 五、车辆管理模块 `/api/v1/vehicle`

### 5.1 车辆档案 `/vehicles`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/vehicle/vehicles` | 车辆列表（支持车牌/车主/类型筛选） |
| GET | `/api/v1/vehicle/vehicles/{id}` | 车辆详情 |
| POST | `/api/v1/vehicle/vehicles` | 新增车辆 |
| PUT | `/api/v1/vehicle/vehicles/{id}` | 修改车辆 |
| DELETE | `/api/v1/vehicle/vehicles/{id}` | 删除车辆 |

**车辆对象：**

```json
{
  "plate_number": "京A12345",
  "owner_name": "张三",
  "owner_id": 5,
  "vehicle_type": "小型汽车",
  "color": "黑色",
  "is_monthly": true,
  "status": 1
}
```

### 5.2 车位管理 `/spots`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/vehicle/spots` | 车位列表（支持区域/状态筛选） |
| GET | `/api/v1/vehicle/spots/statistics` | 车位统计（总数/已占/空闲） |
| POST | `/api/v1/vehicle/spots` | 新增车位 |
| PUT | `/api/v1/vehicle/spots/{id}` | 修改车位 |
| DELETE | `/api/v1/vehicle/spots/{id}` | 删除车位 |

### 5.3 进出记录 `/access-records`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/vehicle/access-records` | 进出记录列表（支持车牌/时间筛选） |
| POST | `/api/v1/vehicle/access-records/enter` | 车辆入场（图片识别+模拟道闸） |
| POST | `/api/v1/vehicle/access-records/exit` | 车辆出场 |

**入场请求体：**

```json
{
  "plate_image": "/uploads/2026/09/plate_xxx.jpg",
  "spot_id": 12
}
```

**入场响应 data：**

```json
{
  "plate_number": "京A12345",
  "vehicle_type": "月卡车辆",
  "is_allowed": true,
  "assigned_spot": "A-012"
}
```

### 5.4 月卡白名单 `/monthly-cards`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/vehicle/monthly-cards` | 月卡列表 |
| POST | `/api/v1/vehicle/monthly-cards` | 新增月卡 |
| PUT | `/api/v1/vehicle/monthly-cards/{id}` | 续费/修改 |
| DELETE | `/api/v1/vehicle/monthly-cards/{id}` | 删除月卡 |

---

## 六、人脸核验通行模块 `/api/v1/access`

### 6.1 通行人员（人脸底库）`/persons`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/access/persons` | 人员列表 |
| GET | `/api/v1/access/persons/{id}` | 人员详情 |
| POST | `/api/v1/access/persons` | 新增人员并采集人脸 |
| PUT | `/api/v1/access/persons/{id}` | 修改人员 |
| DELETE | `/api/v1/access/persons/{id}` | 删除人员及特征 |

**新增人员请求体：**

```json
{
  "user_id": 5,
  "name": "张三",
  "face_image": "/uploads/2026/09/face_xxx.jpg"
}
```

> ⚠️ 人脸原图提取特征后**立即删除**，仅保留特征向量。

### 6.2 人脸核验 `/verify`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/access/verify` | 人脸核验（图片模拟闸机） |
| GET | `/api/v1/access/verify-records` | 核验记录列表 |

**核验请求体：**

```json
{
  "face_image": "/uploads/2026/09/verify_xxx.jpg",
  "device_id": "gate_001"
}
```

**核验响应 data：**

```json
{
  "success": true,
  "person_id": 5,
  "name": "张三",
  "similarity": 0.92,
  "verified_at": "2026-09-08 10:30:00"
}
```

> 核验流程：接收图片 → 调 AI 服务提取特征 → 与底库向量比对 → 写入核验记录 → 返回结果。

---

## 七、访客管理模块 `/api/v1/visitor`

### 7.1 访客邀请 `/invitations`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/visitor/invitations` | 我的邀请列表 |
| POST | `/api/v1/visitor/invitations` | 发起访客邀请 |
| PUT | `/api/v1/visitor/invitations/{id}/cancel` | 取消邀请 |

**邀请请求体：**

```json
{
  "visitor_name": "李四",
  "visitor_phone": "13900139000",
  "visit_date": "2026-09-09",
  "visit_purpose": "商务洽谈",
  "visit_duration": 2
}
```

### 7.2 访客预约 `/appointments`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/visitor/appointments` | 预约列表（支持状态/日期筛选） |
| GET | `/api/v1/visitor/appointments/{id}` | 预约详情 |
| PUT | `/api/v1/visitor/appointments/{id}/approve` | 审批通过 |
| PUT | `/api/v1/visitor/appointments/{id}/reject` | 审批驳回 |

### 7.3 到访核验 `/visits`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/visitor/visits/check-in` | 访客到访核验（扫二维码） |
| POST | `/api/v1/visitor/visits/check-out` | 访客离场 |
| GET | `/api/v1/visitor/visits` | 到访记录列表 |

**到访核验请求体：**

```json
{
  "appointment_code": "VISITOR202609090001"
}
```

---

## 八、设备物联模块 `/api/v1/device`

### 8.1 设备档案 `/devices`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/device/devices` | 设备列表（支持类型/位置/状态筛选） |
| GET | `/api/v1/device/devices/{id}` | 设备详情 |
| POST | `/api/v1/device/devices` | 新增设备 |
| PUT | `/api/v1/device/devices/{id}` | 修改设备 |
| DELETE | `/api/v1/device/devices/{id}` | 删除设备 |
| PUT | `/api/v1/device/devices/{id}/status` | 设备上下线 |

**设备对象：**

```json
{
  "device_code": "GATE_001",
  "name": "东门闸机",
  "type": "gate",
  "location": "园区东门",
  "status": "online",
  "vendor": "海康威视",
  "driver": "mock"
}
```

### 8.2 设备事件 `/events`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/device/events` | 设备事件上报（Mock 与真实硬件共用入口） |
| GET | `/api/v1/device/events` | 事件流水列表 |

**事件上报请求体：**

```json
{
  "device_code": "GATE_001",
  "event_type": "person_pass",
  "event_data": {
    "person_id": 5,
    "direction": "in"
  },
  "event_time": "2026-09-08 10:30:00"
}
```

### 8.3 设备指令 `/commands`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/device/devices/{id}/command` | 下发设备指令（开闸/抓拍等） |

**指令请求体：**

```json
{
  "command": "open_gate",
  "params": { "duration": 5 }
}
```

---

## 九、告警事件中心 `/api/v1/event`

### 9.1 告警事件 `/alarms`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/event/alarms` | 告警列表（支持来源/级别/状态筛选） |
| GET | `/api/v1/event/alarms/{id}` | 告警详情 |
| POST | `/api/v1/event/alarms` | 上报告警（AI/安防/设备调用此入口） |
| PUT | `/api/v1/event/alarms/{id}/acknowledge` | 确认告警 |
| POST | `/api/v1/event/alarms/{id}/dispatch` | 告警派单（调用工单 API 创建工单） |
| GET | `/api/v1/event/alarms/statistics` | 告警统计（大屏用） |

**上报告警请求体：**

```json
{
  "source": "ai_vision",
  "type": "fire_smoke",
  "level": "high",
  "title": "检测到烟火",
  "description": "在 B 栋 3 楼检测到烟雾",
  "image_url": "/uploads/2026/09/alarm_xxx.jpg",
  "location": "B栋3楼",
  "device_code": "CAM_B3_01"
}
```

### 9.2 告警处置日志 `/handle-logs`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/event/alarms/{id}/handle-logs` | 某告警的处置日志 |

---

## 十、报修工单模块 `/api/v1/service`

### 10.1 工单 `/orders`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/service/orders` | 工单列表（支持状态/类型/报修人筛选） |
| GET | `/api/v1/service/orders/{id}` | 工单详情 |
| POST | `/api/v1/service/orders` | 创建工单（小程序报修/告警派单） |
| PUT | `/api/v1/service/orders/{id}/assign` | 派单 |
| PUT | `/api/v1/service/orders/{id}/start` | 开始处理 |
| PUT | `/api/v1/service/orders/{id}/complete` | 处理完成 |
| PUT | `/api/v1/service/orders/{id}/evaluate` | 评价 |

**创建工单请求体：**

```json
{
  "type": "repair",
  "title": "办公室空调故障",
  "description": "3 楼会议室空调不制冷",
  "location": "A栋3楼会议室",
  "reporter_id": 5,
  "image_urls": ["/uploads/2026/09/ticket_xxx.jpg"]
}
```

### 10.2 工单处置记录 `/handle-records`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/service/orders/{id}/handle-records` | 工单处置记录 |

---

## 十一、AI 服务（内部接口，业务后端调用）

> AI 服务独立部署在 `http://ai-service:8001`，业务后端通过 HTTP 调用。

### 11.1 RAG 智能问答 `/rag`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/rag/chat` | 问答（流式响应 SSE） |
| POST | `/api/v1/rag/documents` | 上传知识库文档（异步向量化） |
| GET | `/api/v1/rag/documents` | 知识库文档列表 |
| DELETE | `/api/v1/rag/documents/{id}` | 删除文档 |

**问答请求体：**

```json
{
  "question": "园区停车收费标准是什么？",
  "session_id": "optional-uuid"
}
```

**问答响应（SSE 流）：**

```
data: {"type": "source", "data": [...]}

data: {"type": "token", "data": "根"}

data: {"type": "token", "data": "据"}

...
data: {"type": "done", "data": null}
```

### 11.2 人脸核验 `/face`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/face/extract` | 提取人脸特征向量 |
| POST | `/api/v1/face/compare` | 特征向量比对 |

**提取特征响应 data：**

```json
{
  "feature": [0.123, -0.456, ...],
  "face_detected": true
}
```

### 11.3 图像识别 `/vision`

| 方法 | 路径 | 说明 |
|---|---|---|
| POST | `/api/v1/vision/detect` | 图片目标检测 |

**检测请求体：**

```json
{
  "image_url": "/uploads/2026/09/detect_xxx.jpg",
  "task_type": "fire_smoke"
}
```

**检测响应 data：**

```json
{
  "detected": true,
  "confidence": 0.87,
  "objects": [
    { "label": "smoke", "confidence": 0.87, "bbox": [100, 120, 200, 250] }
  ]
}
```

---

## 十二、大屏统计接口 `/api/v1/dashboard`

| 方法 | 路径 | 说明 |
|---|---|---|
| GET | `/api/v1/dashboard/overview` | 园区总览数据 |
| GET | `/api/v1/dashboard/traffic` | 人车流量趋势（按小时） |
| GET | `/api/v1/dashboard/visitors` | 今日访客统计 |
| GET | `/api/v1/dashboard/alarms` | 实时告警列表 |
| GET | `/api/v1/dashboard/devices` | 设备状态统计 |
| GET | `/api/v1/dashboard/ai-detections` | AI 识别轮播记录 |

**总览响应 data：**

```json
{
  "total_persons": 320,
  "today_visitors": 15,
  "active_alarms": 3,
  "online_devices": 45,
  "parking_usage": { "total": 200, "used": 132, "free": 68 },
  "today_vehicle_entries": 87
}
```

---

> 本文档随骨架代码同步更新，接口有变更请及时更新并通知相关小组。
