# 华为云存储服务控制系统 - 商业版部署指南

## 系统概述

华为云存储服务控制系统商业版是一个全面的企业级解决方案，旨在通过减少硬盘数据碎片化程度，提升存储系统的整体效率。本系统提供了丰富的商业级功能，包括用户认证与权限管理、RESTful API接口、数据可视化、批量处理与调度等，满足企业在存储优化领域的各种需求。

## 系统架构

系统采用模块化设计，主要包括以下核心组件：

1. **用户认证与权限管理模块** (auth_manager.py)
   - 多用户登录和权限控制
   - 基于角色的访问控制
   - 安全的密码存储和验证

2. **RESTful API接口** (api_server.py)
   - 完整的API文档
   - 请求限流和安全控制
   - 支持第三方系统集成

3. **数据库设计与实现** (database.py)
   - 完整的数据模型设计
   - 事务支持和数据完整性保障
   - 高效的数据查询和管理

4. **Web界面基础框架** (web_server.py)
   - 现代化的用户界面
   - 响应式设计，支持多种设备
   - 完整的用户和管理员功能

5. **存储优化算法** (optimizer.py)
   - 贪心算法
   - 动态规划
   - 启发式搜索

## 部署要求

### 硬件要求

- CPU: 4核或更高
- 内存: 8GB或更高
- 硬盘: 50GB可用空间
- 网络: 100Mbps或更高带宽

### 软件要求

- 操作系统: Ubuntu 18.04/20.04/22.04 LTS 或 CentOS 7/8
- Python 3.7或更高版本
- MySQL 5.7或更高版本 / PostgreSQL 10或更高版本
- Nginx 1.14或更高版本 (用于生产环境)

## 安装步骤

### 1. 准备环境

```bash
# 更新系统包
sudo apt update && sudo apt upgrade -y

# 安装依赖
sudo apt install -y python3 python3-pip python3-venv nginx mysql-server

# 创建虚拟环境
python3 -m venv /opt/storage_system_env
source /opt/storage_system_env/bin/activate

# 安装Python依赖
pip install -r requirements.txt
```

### 2. 配置数据库

```bash
# 创建数据库和用户
sudo mysql -e "CREATE DATABASE storage_system CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
sudo mysql -e "CREATE USER 'storage_user'@'localhost' IDENTIFIED BY 'your_secure_password';"
sudo mysql -e "GRANT ALL PRIVILEGES ON storage_system.* TO 'storage_user'@'localhost';"
sudo mysql -e "FLUSH PRIVILEGES;"

# 初始化数据库
python init_database.py
```

### 3. 配置Web服务器

```bash
# 创建Nginx配置
sudo nano /etc/nginx/sites-available/storage_system

# 添加以下配置
server {
    listen 80;
    server_name your_domain.com;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /opt/storage_system/static;
    }
}

# 启用站点
sudo ln -s /etc/nginx/sites-available/storage_system /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 4. 配置系统服务

```bash
# 创建系统服务
sudo nano /etc/systemd/system/storage_system.service

# 添加以下内容
[Unit]
Description=华为云存储服务控制系统
After=network.target mysql.service

[Service]
User=ubuntu
Group=ubuntu
WorkingDirectory=/opt/storage_system
Environment="PATH=/opt/storage_system_env/bin"
ExecStart=/opt/storage_system_env/bin/python web_server.py
Restart=always

[Install]
WantedBy=multi-user.target

# 启用并启动服务
sudo systemctl daemon-reload
sudo systemctl enable storage_system
sudo systemctl start storage_system
```

## 初始配置

### 1. 创建管理员账户

首次启动系统后，访问 http://your_domain.com/register 注册管理员账户。

### 2. 配置系统设置

登录后，访问管理面板配置以下设置：

- 系统名称和描述
- 邮件服务器设置
- 安全策略
- 许可证信息

### 3. 创建角色和权限

在管理面板中创建适合您组织的角色和权限：

- 管理员：拥有所有权限
- 操作员：可以管理和优化存储系统
- 只读用户：只能查看系统状态和报告

## 使用指南

### 1. 创建存储系统

1. 登录系统
2. 点击"创建新存储系统"按钮
3. 填写存储系统信息（名称、描述、硬盘空间、令牌数）
4. 点击"创建"按钮

### 2. 导入存储对象

1. 进入存储系统详情页
2. 点击"导入对象"按钮
3. 上传对象文件（CSV格式）
4. 确认导入

### 3. 优化存储系统

1. 进入存储系统详情页
2. 点击"优化系统"按钮
3. 选择优化算法和参数
4. 点击"开始优化"按钮

### 4. 查看优化结果

1. 进入存储系统详情页
2. 查看"优化历史"部分
3. 点击具体优化任务查看详细结果

## 系统维护

### 备份数据

```bash
# 备份数据库
mysqldump -u storage_user -p storage_system > backup_$(date +%Y%m%d).sql

# 备份配置文件
cp /opt/storage_system/config.ini /opt/storage_system/config.ini.bak
```

### 系统更新

```bash
# 停止服务
sudo systemctl stop storage_system

# 备份当前版本
cp -r /opt/storage_system /opt/storage_system_backup_$(date +%Y%m%d)

# 更新代码
cd /opt/storage_system
git pull

# 更新依赖
source /opt/storage_system_env/bin/activate
pip install -r requirements.txt

# 数据库迁移
python migrate_database.py

# 重启服务
sudo systemctl start storage_system
```

## 故障排除

### 常见问题

1. **系统无法启动**
   - 检查日志: `sudo journalctl -u storage_system`
   - 确认数据库连接正常
   - 验证配置文件正确性

2. **性能问题**
   - 检查数据库索引
   - 优化查询语句
   - 增加服务器资源

3. **登录失败**
   - 重置管理员密码: `python reset_admin_password.py`
   - 检查认证日志

## 联系支持

如需技术支持，请联系：

- 电子邮件: support@example.com
- 电话: +86-10-12345678
- 工单系统: https://support.example.com

## 许可证信息

本系统采用商业许可证，使用前请确保您拥有有效的许可证。许可证包括以下级别：

- 基础版: 支持单用户，最多3个存储系统
- 专业版: 支持10个用户，最多20个存储系统
- 企业版: 无限用户，无限存储系统，附加高级功能

请联系销售团队获取适合您需求的许可证。
