# 模拟数据目录

本目录存放智慧园区综合管理平台各模块的模拟数据，共 20 条记录，覆盖全部 12 个模块。

## 目录结构

```
mock-data/
├── README.md              # 本文件
├── images/                # 图片资源说明
│   └── README.md          # 图片格式与命名规范
├── 01-system/             # 系统管理模块 (7条)
│   ├── 01-users.json
│   ├── 02-roles.json
│   ├── 03-depts.json
│   └── 04-menus.json
├── 02-oa/                 # 办公协同模块 (3条)
│   ├── 01-notices.json
│   ├── 02-approvals.json
│   └── 03-meeting-rooms.json
├── 03-vehicle/            # 车辆管理模块 (4条)
│   ├── 01-vehicles.json
│   ├── 02-spots.json
│   └── 03-access-records.json
├── 04-access/             # 通行安防模块 (1条)
│   └── 01-persons.json
├── 05-visitor/            # 访客管理模块 (1条)
│   └── 01-appointments.json
├── 06-device/             # 设备物联模块 (1条)
│   └── 01-devices.json
├── 07-event/              # 告警事件中心 (1条)
│   └── 01-alarms.json
├── 08-service/            # 报修工单模块 (1条)
│   └── 01-orders.json
├── 09-ai/                 # AI 服务 (1条)
│   └── 01-documents.json
└── 10-dashboard/          # 大屏统计 (1条)
    └── 01-overview.json
```

## 使用说明

- 每条记录的字段与 `docs/API接口定义.md` 中的接口契约严格对齐
- 数据可直接用于开发调试、前端展示、接口联调
- 人脸识别/核验图片请自行准备，详见 `images/README.md`