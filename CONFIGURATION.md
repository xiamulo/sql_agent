# 配置指南

本文档详细说明了如何配置 SQL Agent 项目的各种设置。

## 🔧 配置文件说明

### 1. 数据库配置 (config.ini)

项目使用 `config.ini` 文件来配置数据库连接信息：

```ini
[DBClientInfo]
host=your_database_host          # 数据库主机地址
user=your_username               # 数据库用户名
port=your_port                   # 数据库端口号
password=your_password           # 数据库密码
db=your_database_name           # 数据库名称

[DBClientInfo_yw]               # 备用数据库配置
host=your_database_host_yw
user=your_username_yw
port=your_port_yw
password=your_password_yw
db=your_database_name_yw
```

### 2. OpenAI API 配置 (m_agent/config/key.yaml)

配置 OpenAI API 相关设置：

```yaml
OPENAI_BASE_URL: "https://api.openai.com/v1/"  # OpenAI API 基础 URL
OPENAI_API_KEY: "sk-your-api-key-here"         # OpenAI API 密钥
OPENAI_API_MODEL: "gpt-4o"                     # 使用的模型
MAX_TOKENS: 128000                             # 最大 token 数
RPM: 10                                        # 每分钟请求数限制
TIMEOUT: 10                                    # 请求超时时间（秒）
TEMPERATURE: 0.3                               # 模型温度参数
```

## 🌍 环境变量配置

推荐使用环境变量来管理敏感信息：

### 创建 .env 文件

```bash
cp .env.example .env
```

### 编辑 .env 文件

```bash
# OpenAI API 配置
OPENAI_API_KEY=sk-your-actual-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1/
OPENAI_API_MODEL=gpt-4o

# 数据库配置
DB_HOST=localhost
DB_USER=your_db_user
DB_PORT=3306
DB_PASSWORD=your_db_password
DB_NAME=your_db_name
```

## 🔒 安全最佳实践

### 1. 敏感信息保护

- **永远不要**将真实的 API 密钥或数据库密码提交到版本控制系统
- 使用 `.gitignore` 文件排除敏感配置文件
- 在生产环境中使用环境变量或安全的密钥管理服务

### 2. 数据库安全

- 创建专用的数据库用户，避免使用 root 用户
- 为数据库用户分配最小必要权限
- 使用强密码并定期更换
- 在生产环境中启用 SSL 连接

### 3. API 密钥管理

- 定期轮换 API 密钥
- 监控 API 使用情况，设置使用限制
- 使用不同的密钥用于开发、测试和生产环境

## 🚀 部署配置

### 开发环境

```bash
# 设置环境变量
export OPENAI_API_KEY="your-dev-api-key"
export DB_HOST="localhost"
export DB_PASSWORD="dev-password"

# 启动服务
python m_agent/sql_agent.py
```

### 生产环境

```bash
# 使用生产环境配置
export OPENAI_API_KEY="your-prod-api-key"
export DB_HOST="prod-db-host"
export DB_PASSWORD="secure-prod-password"

# 启动服务
python main2.py
```

## 🔍 配置验证

### 检查数据库连接

```python
from util.sqlutil import select_data_sql

try:
    result = select_data_sql("SELECT 1")
    print("数据库连接成功")
except Exception as e:
    print(f"数据库连接失败: {e}")
```

### 检查 OpenAI API

```python
import os
from metagpt.config import CONFIG

if CONFIG.openai_api_key:
    print("OpenAI API 密钥已配置")
else:
    print("请配置 OpenAI API 密钥")
```

## 📝 配置模板

### Docker 环境变量文件

```bash
# docker.env
OPENAI_API_KEY=sk-your-api-key
OPENAI_BASE_URL=https://api.openai.com/v1/
DB_HOST=db
DB_USER=sqluser
DB_PASSWORD=sqlpassword
DB_NAME=sqldb
```

### Kubernetes ConfigMap

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: sql-agent-config
data:
  OPENAI_BASE_URL: "https://api.openai.com/v1/"
  OPENAI_API_MODEL: "gpt-4o"
  DB_HOST: "mysql-service"
  DB_PORT: "3306"
  DB_NAME: "sqldb"
```

## ❓ 常见问题

### Q: 如何更换 OpenAI API 提供商？

A: 修改 `OPENAI_BASE_URL` 和 `OPENAI_API_KEY` 指向新的 API 提供商。

### Q: 如何配置多个数据库？

A: 在 `config.ini` 中添加新的数据库配置段，并在代码中相应地调用。

### Q: 如何在 Docker 中使用配置？

A: 使用 Docker 的环境变量功能或挂载配置文件到容器中。

---

如有其他配置问题，请参考项目文档或提交 Issue。
