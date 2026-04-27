# 蜀来驰二手车网站 - 快速开始

## 本地运行（3分钟快速启动）

### 第一步：安装依赖
```bash
cd 蜀来驰二手车网站
pip install flask flask-sqlalchemy werkzeug
```

### 第二步：启动网站
```bash
python app.py
```

### 第三步：访问网站
- 🌐 网站首页：http://localhost:5000
- 🔐 后台管理：http://localhost:5000/admin/login

## 默认账号
- 用户名：admin
- 密码：slc123456

## 功能概览

### 前台功能
- ✅ 首页轮播图展示
- ✅ 精选车源展示（首页6辆）
- ✅ 车源列表页
- ✅ 价格筛选（2万以下/2-5万/5-10万）
- ✅ 品牌筛选
- ✅ 车辆详情页（多图、检测报告）
- ✅ 联系方式页面

### 后台功能
- ✅ 仪表盘（统计概览）
- ✅ 车辆管理（增删改查、上下架）
- ✅ 轮播图管理
- ✅ 网站设置
- ✅ 密码修改

## 目录结构

```
蜀来驰二手车网站/
├── app.py              # 主应用
├── requirements.txt    # 依赖
├── README.md           # 说明文档
├── DEPLOY.md           # 部署指南
├── static/
│   ├── css/style.css   # 样式
│   ├── images/         # 图片
│   └── uploads/        # 上传文件
└── templates/
    ├── index.html      # 首页
    ├── cars.html       # 列表页
    ├── car_detail.html # 详情页
    ├── contact.html    # 联系页
    └── admin/          # 后台页面
```

## 常见问题

Q: 网站打不开？
A: 检查5000端口是否被占用，尝试更换端口

Q: 图片上传失败？
A: 检查static/uploads目录是否存在和读写权限

Q: 后台无法登录？
A: 检查数据库是否正确创建，账号密码是否正确

## 截图预览

网站采用现代化设计风格：
- 🎨 红色渐变主题色
- 📱 完全响应式设计
- ✨ 流畅的动画效果
- 🖼️ 支持多图轮播
