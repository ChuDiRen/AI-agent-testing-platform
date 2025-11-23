# 基础服务一键安装脚本

自动化安装和配置 MySQL、Redis、PostgreSQL、MinIO、RabbitMQ 的脚本集合。

## 功能特性

- ✅ 自动检测操作系统（Ubuntu/Debian、CentOS/RHEL、macOS）
- ✅ 一键安装 MySQL、Redis、PostgreSQL、MinIO、RabbitMQ
- ✅ 自动配置数据目录和日志目录
- ✅ 自动配置防火墙端口（支持 firewalld/ufw/iptables）
- ✅ 统一密码配置（admin123456）
- ✅ 创建测试数据库和用户
- ✅ 提供卸载脚本
- ✅ **全自动执行，无需交互确认**

## 支持的操作系统

- Ubuntu 18.04+
- Debian 10+
- CentOS 7+
- RHEL 7+
- macOS 10.15+

## 快速开始

### 一键安装所有服务

```bash
sudo bash install-all.sh
```

### 单独安装某个服务

```bash
# 安装 MySQL
sudo bash install-mysql.sh

# 安装 Redis
sudo bash install-redis.sh

# 安装 PostgreSQL
sudo bash install-postgres.sh

# 安装 MinIO
sudo bash install-minio.sh

# 安装 RabbitMQ
sudo bash install-rabbitmq.sh
```

## 默认配置

> **统一密码**: `admin123456`

### MySQL
- **端口**: 3306
- **Root 密码**: `admin123456`
- **测试数据库**: testdb
- **测试用户**: testuser / admin123456

### Redis
- **端口**: 6379
- **密码**: `admin123456`
- **最大内存**: 256MB
- **持久化**: RDB + AOF

### PostgreSQL
- **端口**: 5432
- **超级用户密码**: `admin123456`
- **测试数据库**: testdb
- **测试用户**: testuser / admin123456

### MinIO
- **API 端口**: 9000
- **控制台端口**: 9001
- **Root 用户**: admin
- **Root 密码**: `admin123456`
- **默认桶**: test-bucket, uploads

### RabbitMQ
- **AMQP 端口**: 5672
- **管理界面端口**: 15672
- **管理员用户**: admin
- **管理员密码**: `admin123456`
- **虚拟主机**: /

## 连接示例

### MySQL

```bash
# 命令行连接
mysql -uroot -p'admin123456'

# Python 连接
import pymysql
conn = pymysql.connect(
    host='localhost',
    port=3306,
    user='testuser',
    password='admin123456',
    database='testdb'
)
```

### Redis

```bash
# 命令行连接
redis-cli -a 'admin123456'

# Python 连接
import redis
r = redis.Redis(
    host='localhost',
    port=6379,
    password='admin123456',
    decode_responses=True
)
```

### PostgreSQL

```bash
# 命令行连接
export PGPASSWORD='admin123456'
psql -h localhost -U postgres

# Python 连接
import psycopg2
conn = psycopg2.connect(
    host='localhost',
    port=5432,
    database='testdb',
    user='testuser',
    password='admin123456'
)
```

### MinIO

```bash
# 使用 mc 客户端
mc alias set local http://localhost:9000 admin admin123456
mc ls local/

# Python 连接
from minio import Minio
client = Minio(
    'localhost:9000',
    access_key='admin',
    secret_key='admin123456',
    secure=False
)

# 上传文件示例
client.fput_object('test-bucket', 'file.txt', '/path/to/file.txt')
```

### RabbitMQ

```bash
# 访问管理界面
# 浏览器打开: http://localhost:15672
# 用户名: admin
# 密码: admin123456

# Python 连接 (pika)
import pika
credentials = pika.PlainCredentials('admin', 'admin123456')
connection = pika.BlockingConnection(
    pika.ConnectionParameters('localhost', 5672, '/', credentials)
)
channel = connection.channel()

# Python 连接 (aio-pika 异步)
import aio_pika
connection = await aio_pika.connect_robust(
    'amqp://admin:admin123456@localhost:5672/'
)
```

## 目录结构

安装后会创建以下目录：

```
AI-agent-testing-platform/
├── database-setup/                      # 安装脚本目录
│   ├── install-all.sh                   # 一键安装所有服务
│   ├── install-mysql.sh                 # MySQL 安装脚本
│   ├── install-redis.sh                 # Redis 安装脚本
│   ├── install-postgres.sh              # PostgreSQL 安装脚本
│   ├── install-minio.sh                 # MinIO 安装脚本
│   ├── install-rabbitmq.sh              # RabbitMQ 安装脚本
│   ├── set-static-ip-192.168.1.128.sh   # 静态IP配置脚本
│   ├── uninstall.sh                     # 卸载脚本
│   └── README.md                        # 说明文档
├── database-data/           # 数据存储目录
│   ├── mysql/
│   ├── redis/
│   ├── postgres/
│   └── minio/
└── database-logs/           # 日志目录
    ├── mysql/
    ├── redis/
    ├── postgres/
    └── minio/
```

## 卸载

```bash
sudo bash uninstall.sh
```

⚠️ **警告**: 卸载脚本将自动删除所有服务及其数据，无需确认，请谨慎操作！

## 静态IP配置

如果需要配置服务器为固定IP地址，可以使用提供的静态IP配置脚本。

### 配置固定IP: 192.168.1.128

```bash
sudo bash set-static-ip-192.168.1.128.sh
```

### 配置参数

| 参数 | 值 |
|------|------|
| IP地址 | 192.168.1.128 |
| 子网掩码 | 255.255.255.0 (/24) |
| 网关 | 192.168.1.1 |
| DNS1 | 8.8.8.8 |
| DNS2 | 114.114.114.114 |

### 功能特性

- ✅ 自动检测网络接口（eth0/ens33/enp0s3等）
- ✅ 自动备份原网络配置
- ✅ 支持 Ubuntu/Debian (netplan/interfaces)
- ✅ 支持 CentOS/RHEL (nmcli/network-scripts)
- ✅ 自动配置DNS服务器
- ✅ 配置后自动验证网络连通性

### 使用步骤

1. **执行脚本**
   ```bash
   cd database-setup
   sudo bash set-static-ip-192.168.1.128.sh
   ```

2. **自动执行**
   - 脚本会自动检测网络接口
   - 自动备份原配置
   - 自动应用新的网络配置
   - 自动验证网络连通性
   - **无需任何交互确认**

3. **重新连接**
   - 如果通过SSH连接，连接可能会断开
   - 使用新IP `192.168.1.128` 重新连接

### 配置验证

```bash
# 查看IP地址
ip addr show

# 查看路由
ip route show

# 查看DNS配置
cat /etc/resolv.conf

# 测试网关连通性
ping -c 4 192.168.1.1

# 测试外网连通性
ping -c 4 www.baidu.com
```

### 恢复配置

如果需要恢复原配置，可以使用备份文件：

```bash
# 备份文件位于
ls -la /root/network-backup-*

# 恢复 Ubuntu/Debian (netplan)
cp /root/network-backup-*/netplan/*.yaml /etc/netplan/
netplan apply

# 恢复 CentOS/RHEL
cp /root/network-backup-*/ifcfg-* /etc/sysconfig/network-scripts/
systemctl restart network
```

## 防火墙配置

脚本会自动检测并配置防火墙，开放以下端口：

### 自动开放的端口

| 服务 | 端口 | 说明 |
|------|------|------|
| MySQL | 3306 | 数据库连接端口 |
| Redis | 6379 | 缓存服务端口 |
| PostgreSQL | 5432 | 数据库连接端口 |
| MinIO | 9000 | API 端口 |
| MinIO | 9001 | 控制台端口 |
| RabbitMQ | 5672 | AMQP 协议端口 |
| RabbitMQ | 15672 | 管理界面端口 |

### 支持的防火墙类型

- **firewalld** (CentOS/RHEL/Fedora)
- **ufw** (Ubuntu/Debian)
- **iptables** (通用 Linux)

### 手动配置防火墙

如果需要手动配置，可以使用以下命令：

```bash
# firewalld
firewall-cmd --permanent --add-port=3306/tcp
firewall-cmd --permanent --add-port=6379/tcp
firewall-cmd --permanent --add-port=5432/tcp
firewall-cmd --permanent --add-port=9000/tcp
firewall-cmd --permanent --add-port=9001/tcp
firewall-cmd --permanent --add-port=5672/tcp
firewall-cmd --permanent --add-port=15672/tcp
firewall-cmd --reload

# ufw
ufw allow 3306/tcp
ufw allow 6379/tcp
ufw allow 5432/tcp
ufw allow 9000/tcp
ufw allow 9001/tcp
ufw allow 5672/tcp
ufw allow 15672/tcp

# iptables
iptables -I INPUT -p tcp --dport 3306 -j ACCEPT
iptables -I INPUT -p tcp --dport 6379 -j ACCEPT
iptables -I INPUT -p tcp --dport 5432 -j ACCEPT
iptables -I INPUT -p tcp --dport 9000 -j ACCEPT
iptables -I INPUT -p tcp --dport 9001 -j ACCEPT
iptables -I INPUT -p tcp --dport 5672 -j ACCEPT
iptables -I INPUT -p tcp --dport 15672 -j ACCEPT
iptables-save > /etc/sysconfig/iptables
```

### 查看防火墙状态

```bash
# firewalld
firewall-cmd --list-ports

# ufw
ufw status

# iptables
iptables -L -n | grep ACCEPT
```

## 安全建议

1. **修改默认密码**: 安装后请立即修改默认密码
2. **防火墙配置**: 根据需要配置防火墙规则
3. **定期备份**: 设置定期备份策略
4. **权限管理**: 合理配置数据库用户权限

## 故障排查

### MySQL 无法启动
```bash
# 查看日志
tail -f ../database-logs/mysql/error.log

# 检查服务状态
systemctl status mysql
```

### Redis 连接失败
```bash
# 检查 Redis 是否运行
redis-cli -a 'admin123456' ping

# 查看日志
tail -f ../database-logs/redis/redis.log
```

### PostgreSQL 认证失败
```bash
# 检查 pg_hba.conf 配置
cat /etc/postgresql/15/main/pg_hba.conf

# 重启服务
systemctl restart postgresql
```

### MinIO 无法访问
```bash
# 检查服务状态
systemctl status minio

# 查看日志
journalctl -u minio -f

# 测试连接
mc admin info local
```

### RabbitMQ 连接失败
```bash
# 检查服务状态
systemctl status rabbitmq-server

# 查看节点状态
rabbitmqctl status

# 查看用户列表
rabbitmqctl list_users

# 重启服务
systemctl restart rabbitmq-server
```

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！
