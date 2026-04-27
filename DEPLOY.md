# 蜀来驰二手车网站 - 云端部署指南

## 部署方案

### 方案一：阿里云/腾讯云部署

#### 1. 服务器准备
- 推荐配置：2核2G内存
- 操作系统：Ubuntu 20.04 / CentOS 7+
- 安装 Python 3.8+

#### 2. 项目部署步骤

```bash
# 1. 连接服务器
ssh root@your-server-ip

# 2. 安装依赖
apt update && apt upgrade -y
apt install python3 python3-pip nginx -y

# 3. 上传项目（可以使用scp、rsync或git）
cd /var/www
scp -r ./蜀来驰二手车网站 root@your-server-ip:/var/www/

# 4. 安装Python依赖
cd /var/www/蜀来驰二手车网站
pip3 install -r requirements.txt

# 5. 配置Gunicorn
pip3 install gunicorn

# 6. 测试运行
python3 app.py &
# 访问 http://your-server-ip:5000 测试

# 7. 配置Nginx反向代理
cat > /etc/nginx/sites-available/slc-car << EOF
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias /var/www/蜀来驰二手车网站/static;
        expires 30d;
    }
}
EOF

# 8. 启用站点
ln -s /etc/nginx/sites-available/slc-car /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# 9. 配置SSL证书（推荐使用Let's Encrypt）
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

#### 3. 使用PM2管理进程（推荐）

```bash
# 安装PM2
npm install -g pm2

# 启动应用
cd /var/www/蜀来驰二手车网站
pm2 start gunicorn --name "slc-car" -- -w 4 -b 127.0.0.1:5000 app:app

# 设置开机自启
pm2 save
pm2 startup

# 查看状态
pm2 list
pm2 logs slc-car
```

---

### 方案二：使用Docker部署

#### 1. 创建Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

#### 2. 创建docker-compose.yml

```yaml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - ./static/uploads:/app/static/uploads
    restart: unless-stopped
```

#### 3. 部署命令

```bash
docker-compose up -d
```

---

### 方案三：使用宝塔面板部署

1. 安装宝塔面板
2. 创建Python项目
3. 上传代码
4. 配置虚拟环境
5. 添加反向代理到5000端口
6. 配置网站域名SSL

---

## 数据备份

### 备份数据库
```bash
# 备份SQLite数据库
cp shulaichi.db shulaichi.db.backup.$(date +%Y%m%d)
```

### 备份整个项目
```bash
# 使用rsync备份
rsync -avz --exclude='__pycache__' --exclude='*.pyc' /var/www/蜀来驰二手车网站 /backup/
```

---

## 安全建议

1. **修改默认密码**：首次部署后立即修改admin密码
2. **配置防火墙**：仅开放80/443端口
3. **启用HTTPS**：使用SSL证书加密传输
4. **定期备份**：设置自动备份任务
5. **限制上传**：图片大小限制已在代码中设置

---

## 故障排查

### 网站无法访问
```bash
# 检查Gunicorn进程
pm2 list
pm2 logs slc-car

# 检查端口占用
netstat -tlnp | grep 5000

# 检查Nginx日志
tail -f /var/log/nginx/error.log
```

### 数据库问题
```bash
# 重新初始化数据库
rm shulaichi.db
python3 app.py
```

---

## 联系方式

如需技术支持，请联系开发者。
