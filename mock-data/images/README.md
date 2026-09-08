# 图片资源说明

请自行准备以下图片，放入 `backend/static/uploads/` 对应目录。

---

## 1. 人脸底库采集图片

| 用途 | 路径示例 | 格式要求 | 说明 |
|---|---|---|---|
| 员工人脸录入 | `backend/static/uploads/faces/zhangsan.jpg` | JPG/PNG，建议 640x640 以上 | 正面免冠、光线均匀、双眼可见、无遮挡 |
| 员工人脸录入 | `backend/static/uploads/faces/lisi.jpg` | 同上 | 同上 |

**规范：**
- 格式：`.jpg` 或 `.png`
- 分辨率：建议不低于 640×640 像素
- 内容：单人正面照，面部占画面 1/3 以上
- 文件命名：`{姓名拼音}.jpg`，如 `zhangsan.jpg`
- 每人仅需 1 张照片（InsightFace 提取特征向量后原图建议删除）

## 2. 人脸核验图片

| 用途 | 路径示例 | 格式要求 | 说明 |
|---|---|---|---|
| 闸机核验抓拍 | `backend/static/uploads/verify/verify_001.jpg` | JPG/PNG，建议 640x640 以上 | 模拟闸机抓拍，可包含半身或全身，面部清晰 |
| 闸机核验抓拍 | `backend/static/uploads/verify/verify_002.jpg` | 同上 | 同上 |

**规范：**
- 格式：`.jpg` 或 `.png`
- 分辨率：建议不低于 640×640 像素
- 内容：可包含半身/全身，但面部需足够清晰以完成比对
- 文件命名：`verify_{序号}.jpg`

## 3. 车辆车牌图片

| 用途 | 路径示例 | 格式要求 | 说明 |
|---|---|---|---|
| 车牌识别入场 | `backend/static/uploads/plates/plate_001.jpg` | JPG/PNG，建议 1920x1080 | 模拟道闸抓拍，车牌清晰可见 |
| 车牌识别入场 | `backend/static/uploads/plates/plate_002.jpg` | 同上 | 同上 |

**规范：**
- 格式：`.jpg` 或 `.png`
- 分辨率：建议 1920×1080 或以上
- 内容：车辆正面或尾部照片，车牌区域清晰
- 文件命名：`plate_{序号}.jpg`

## 4. 告警/识别图片

| 用途 | 路径示例 | 格式要求 | 说明 |
|---|---|---|---|
| 消防通道占用 | `backend/static/uploads/alarms/alarm_fire_001.jpg` | JPG/PNG | 包含车辆/杂物占用消防通道的画面 |
| 烟火检测 | `backend/static/uploads/alarms/alarm_smoke_001.jpg` | JPG/PNG | 包含火焰或烟雾的画面 |
| 人群聚集 | `backend/static/uploads/alarms/alarm_crowd_001.jpg` | JPG/PNG | 包含多人聚集的场景 |

**规范：**
- 格式：`.jpg` 或 `.png`
- 分辨率：建议 1920×1080
- 文件命名：`alarm_{类型}_{序号}.jpg`

## 5. 报修工单图片

| 用途 | 路径示例 | 格式要求 | 说明 |
|---|---|---|---|
| 故障现场照片 | `backend/static/uploads/tickets/ticket_001.jpg` | JPG/PNG | 设施故障现场照片，如空调、照明等 |

**规范：**
- 格式：`.jpg` 或 `.png`
- 分辨率：建议 1080×1920（手机竖屏拍摄）
- 文件命名：`ticket_{序号}.jpg`

---

## 汇总

| 类别 | 需准备数量 | 存放目录 |
|---|---|---|
| 人脸底库照片 | 2 张 | `backend/static/uploads/faces/` |
| 核验抓拍照片 | 2 张 | `backend/static/uploads/verify/` |
| 车牌照片 | 2 张 | `backend/static/uploads/plates/` |
| 告警识别照片 | 3 张 | `backend/static/uploads/alarms/` |
| 报修现场照片 | 1 张 | `backend/static/uploads/tickets/` |
| **合计** | **10 张** | — |