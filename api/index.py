"""
Vercel Serverless Functions 入口
将Flask应用适配到Vercel Serverless环境
"""

from app import app, db
import os

# 确保数据库在serverless环境中初始化
with app.app_context():
    db.create_all()
    
# Vercel需要导出 'app' 变量
handler = app
