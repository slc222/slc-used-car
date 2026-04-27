# Deta Cloud 部署配置
# 完全免费，支持持久化存储
# 访问 https://deta.sh 注册并安装 CLI

# 1. 安装 Deta CLI
# curl -fsSL https://get.deta.dev/space-cli.sh | sh

# 2. 登录
# space login

# 3. 创建新项目
# cd 蜀来驰二手车网站
# deta new --python

# 4. 配置微运行
# deta micro set --name app --file app.py

# 5. 查看日志
# deta logs

# 6. 获取访问地址
# deta edges create

# 注意：Deta免费层限制：
# - 每月100GB带宽
# - 2GB存储
# - 每天10万次请求

pythonVersion: "3.11"
runtime: python
entrypoint: app:app
