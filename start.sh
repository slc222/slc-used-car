#!/bin/bash

# 蜀来驰二手车网站 - 启动脚本

echo "========================================"
echo "  蜀来驰二手车网站 启动脚本"
echo "========================================"
echo ""

# 检查Python版本
python_version=$(python3 --version 2>&1)
echo "Python版本: $python_version"

# 创建必要的目录
echo "创建目录..."
mkdir -p static/uploads/cars
mkdir -p static/uploads/sliders
mkdir -p static/images
echo "目录创建完成"

# 安装依赖
echo "安装Python依赖..."
pip install -r requirements.txt

# 启动应用
echo ""
echo "启动网站..."
echo "前台地址: http://localhost:5000"
echo "后台地址: http://localhost:5000/admin/login"
echo "用户名: admin"
echo "密码: slc123456"
echo ""
echo "按 Ctrl+C 停止服务"
echo "========================================"

python3 app.py
