# SQL Agent - 智能数据分析代理系统

基于 MetaGPT 框架开发的智能体 SQL 代理系统，专为物流行业数据分析而设计。该系统通过多角色协作的方式，将自然语言查询需求转换为精确的 SQL 查询语句，并提供智能化的数据分析结果。

## 🚀 项目特色

- **多角色协作架构**：基于 MetaGPT 框架，实现数据分析师、数据库管理员、测试工程师等多个智能角色的协同工作
- **自然语言处理**：支持中文自然语言查询，自动理解用户意图并转换为 SQL 语句
- **智能 API 选择**：内置多种预定义 API，根据用户需求自动选择最合适的数据获取方式
- **实时任务处理**：支持异步任务处理，可同时处理多个查询请求
- **物流业务专用**：针对物流行业特点，内置运单、提单、船司等业务相关的查询模板

## 🏗️ 系统架构

### 核心角色 (Roles)

1. **Sqltool (数据分析师3)**
   - 负责理解用户需求，选择合适的 API
   - 根据需求匹配预定义的数据获取接口

2. **Sqlproject (数据分析师)**
   - 分析用户数据需求，转化为具体的数据查询请求
   - 确保需求的准确性和完整性

3. **SqlCoder (数据库管理员)**
   - 根据数据分析师的需求编写 MySQL 查询语句
   - 确保 SQL 语句的正确性和效率

4. **SqlTester (QA工程师)**
   - 检验 SQL 语句的语法正确性和逻辑一致性
   - 验证查询结果的准确性

5. **SqlSummary (数据分析工程师)**
   - 对查询结果进行深入分析和计算
   - 将分析结果转化为易理解的文本报告

### 核心功能模块

- **API 工具集**：包含运单查询、提单时效、价格对比等多种预定义 API
- **智能 SQL 生成**：基于数据库表结构自动生成优化的 SQL 查询语句
- **结果分析引擎**：对查询结果进行统计分析和业务洞察
- **任务管理系统**：支持任务队列、状态跟踪和结果推送

## 📦 安装部署

### 环境要求

- Python 3.8+
- MySQL 数据库
- Redis (可选，用于缓存)

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置文件

#### 1. 数据库配置

编辑 `config.ini` 文件，配置数据库连接信息：

```ini
[DBClientInfo]
host=your_database_host
user=your_username
port=your_port
password=your_password
db=your_database_name

[DBClientInfo_yw]
host=your_database_host_yw
user=your_username_yw
port=your_port_yw
password=your_password_yw
db=your_database_name_yw
```

#### 2. OpenAI API 配置

编辑 `m_agent/config/key.yaml` 文件，配置 OpenAI API 信息：

```yaml
OPENAI_BASE_URL: "your_openai_api_base_url"
OPENAI_API_KEY: "your_openai_api_key"
OPENAI_API_MODEL: "gpt-4o"
MAX_TOKENS: 128000
RPM: 10
TIMEOUT: 10
TEMPERATURE: 0.3
```

#### 3. 环境变量配置 (推荐)

您也可以使用环境变量来配置敏感信息。复制 `.env.example` 文件为 `.env` 并填入您的配置：

```bash
cp .env.example .env
# 然后编辑 .env 文件
```

### 启动服务

1. **启动 SQL 代理服务**：
```bash
python m_agent/sql_agent.py
```

2. **启动 Web API 服务**：
```bash
python main2.py
```

服务将在 `http://localhost:8006` 启动。

## 🔧 使用方法

### API 接口

#### 1. 提交查询请求

**POST** `/chat_msg`

```json
{
    "content": "这周会到港的提单有哪些",
    "task_id": "unique_task_id"
}
```

#### 2. 查询任务状态

**POST** `/check_task`

```json
{
    "task_id": "unique_task_id"
}
```

### 支持的查询类型

- **运单查询**：查询特定运单的状态和轨迹信息
- **提单时效**：分析提单的时效性和到港情况
- **价格对比**：比较不同船司的运费报价
- **时间分析**：计算运输过程中各环节的耗时
- **数据统计**：生成各类业务数据的统计报告

### 查询示例

```
# 时效查询
"这周会到港的提单有哪些"

# 价格分析
"哪家船司的海运费最便宜"

# 运单跟踪
"运单ABC123的当前状态"

# 时间分析
"EMC船司一般几天能将订单送到"
```

## 🛠️ 开发指南

### 项目结构

```
sql_agent/
├── m_agent/                 # 核心代理模块
│   ├── action/             # 动作定义
│   ├── rule/               # 角色定义
│   ├── config/             # 配置文件
│   └── logs/               # 日志文件
├── metagpt/                # MetaGPT 框架
├── util/                   # 工具模块
├── spider/                 # 爬虫模块
├── test/                   # 测试文件
├── main.py               # Web API 服务
├── config.ini             # 配置文件
└── requirements.txt       # 依赖列表
```

### 添加新的 API

1. 在 `m_agent/action/SqlprojectTool.py` 中添加新的 API 定义
2. 实现对应的数据获取方法
3. 更新 `available_functions` 字典

### 自定义角色

继承 `metagpt.roles.Role` 类，实现自定义的智能角色：

```python
from metagpt.roles import Role
from metagpt.actions import Action

class CustomRole(Role):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_actions([CustomAction])
    
    async def _act(self):
        # 实现角色行为逻辑
        pass
```

## 📊 性能特点

- **并发处理**：支持多任务并发执行
- **智能缓存**：减少重复查询的响应时间
- **错误恢复**：具备自动重试和错误处理机制
- **资源优化**：合理的内存和数据库连接管理

## 🤝 贡献指南

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🙏 致谢

- [MetaGPT](https://github.com/geekan/MetaGPT) - 提供了强大的多智能体协作框架
- 感谢所有为这个项目做出贡献的开发者

## 🔒 安全注意事项

- **敏感信息保护**：请勿将 API 密钥、数据库密码等敏感信息提交到版本控制系统
- **配置文件**：使用 `.env` 文件或环境变量来管理敏感配置
- **权限控制**：确保数据库用户具有适当的权限，避免使用 root 用户
- **网络安全**：在生产环境中使用 HTTPS 和适当的防火墙配置

## 📞 联系方式

如有问题或建议，请通过以下方式联系：

- 提交 Issue
- 发送邮件至项目维护者

---

**注意**：本项目专为物流行业数据分析场景设计，使用前请确保已正确配置数据库连接和相关权限。
