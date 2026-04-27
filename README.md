# 蜀来驰二手车展示网站

基于 Flask 的二手车展示网站，包含前台展示和后台管理系统。

## 功能特性

### 前台展示
- 🚗 首页轮播图展示
- 🚗 精选车源展示
- 🚗 车源列表（支持价格、品牌筛选）
- 🚗 车辆详情页（含多图展示、检测报告）
- 🚗 联系方式页面
- 🚗 响应式设计，手机端友好

### 后台管理
- 🔐 管理员登录验证
- 📊 数据统计仪表盘
- 🚙 车辆管理（添加、编辑、删除、上下架）
- 🖼️ 轮播图管理
- ⚙️ 网站设置
- 🔑 密码修改

## 技术栈

- **后端**: Python Flask
- **数据库**: SQLite
- **前端**: HTML5 + CSS3 + JavaScript
- **图标**: Font Awesome 6.4
- **部署**: Gunicorn

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行网站

```bash
python app.py
```

网站将在 http://localhost:5000 启动

### 3. 访问后台

- 地址: http://localhost:5000/admin/login
- 用户名: admin
- 密码: slc123456

## 目录结构

```
蜀来驰二手车网站/
├── app.py                  # 主应用文件
├── requirements.txt         # Python依赖
├── README.md               # 说明文档
├── static/
│   ├── css/
│   │   └── style.css       # 全局样式
│   └── uploads/            # 上传文件目录
│       ├── cars/            # 车辆图片
│       └── sliders/         # 轮播图
└── templates/
    ├── index.html          # 首页
    ├── cars.html           # 车源列表页
    ├── car_detail.html     # 车辆详情页
    ├── contact.html        # 联系方式页
    └── admin/              # 后台模板
        ├── login.html
        ├── dashboard.html
        ├── cars.html
        ├── car_form.html
        ├── settings.html
        ├── sliders.html
        └── password.html
```

## 部署说明

### 生产环境部署

1. 使用 Gunicorn 运行:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

2. 可以使用 Nginx 反向代理

3. 建议使用 PM2 管理进程:
```bash
pm2 start gunicorn --name "slc-car" -- -w 4 -b 0.0.0.0:5000 app:app
```

## 默认账号

- 用户名: admin
- 密码: slc123456

⚠️ 请在部署后及时修改默认密码！

## 注意事项

1. 上传的图片存储在 `static/uploads/` 目录
2. 数据库文件为 `shulaichi.db`（SQLite）
3. 首次运行会自动创建数据库和示例数据
4. 建议定期备份数据库文件

## 联系方式

如有问题，请联系开发者。
