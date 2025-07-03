# SQL Agent - 智能数据分析

基于 MetaGPT 框架开发的智能体数据分析，专为物流行业数据分析而设计。该系统通过多角色协作的方式，将自然语言查询需求转换为精确的 SQL 查询语句，并提供智能化的数据分析结果。

## 🚀 项目特色

- **多角色协作架构**：基于 MetaGPT 框架，实现数据分析师、数据库管理员、测试工程师等多个智能角色的协同工作
- **自然语言处理**：支持中文自然语言查询，自动理解用户意图并转换为 SQL 语句
- **智能 API 选择**：内置多种预定义 API，根据用户需求自动选择最合适的数据获取方式
- **智能代码生成**：自动生成和执行 Python 数据处理代码，支持复杂的文本分析和数据处理任务
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

6. **SimpleCoder (Python 代码生成专家)**
   - 基于数据库表结构理解用户需求
   - 将业务需求转化为清晰的数据查询描述
   - 为数据库管理员提供精确的数据需求规格

7. **RunnableCoder (智能代码执行专家)**
   - 集成代码生成和执行能力的复合型智能体
   - 自动生成 Python 数据处理代码
   - 实时执行代码并验证结果
   - 支持 NLP 文本处理、正则表达式、jieba 分词等多种技术
   - 具备代码自动修复和优化能力

### 核心功能模块

- **API 工具集**：包含运单查询、提单时效、价格对比等多种预定义 API
- **智能 SQL 生成**：基于数据库表结构自动生成优化的 SQL 查询语句
- **智能代码生成与执行**：
  - 自动生成 Python 数据处理代码
  - 支持实时代码执行和结果验证
  - 集成 NLP 处理能力（正则表达式、jieba 分词等）
  - 具备代码错误检测和自动修复功能
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
```json
{
    "content": "分析一下为什么这两个月的提单数量比之前少",
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
- **智能代码处理**：
  - 自动生成数据处理和分析代码
  - 支持文本提取、清洗和分析
  - NLP 任务处理（分词、实体识别等）
  - 数据格式转换和处理

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

# 数据分析
"分析一下为什么这两个月的提单数量比之前少"

# 智能代码生成示例
"帮我写一个Python函数提取文本中的所有邮箱地址"
"生成代码来清洗和处理CSV文件中的数据"
"写一个函数来分析文本的情感倾向"
```

## 🛠️ 开发指南



### 智能代码生成功能

系统集成了强大的代码生成和执行能力：

#### SimpleCoder (代码生成专家)
- 基于数据库表结构理解用户需求
- 将自然语言需求转化为精确的数据查询描述
- 为后续的 SQL 生成提供清晰的需求规格

#### RunnableCoder (代码执行专家)
- **双重能力**：集成代码生成 (`SimpleWriteCode`) 和代码执行 (`SimpleRunCode`)
- **执行模式**：按顺序执行模式 (`by_order`)，先生成代码再执行
- **技术支持**：
  - NLP 文本处理（正则表达式、jieba 分词）
  - 自动代码错误检测和修复
  - 支持多种 Python 数据处理库

#### 代码执行引擎特性
```python
# 支持的功能
- 动态代码执行和结果验证
- 自动错误检测和代码修复
- NLP 处理能力（不能同时使用正则和 jieba）
- 返回结构化的 list 数据
- 实时代码优化和性能调整
```

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
- **代码执行优化**：
  - 动态代码生成和实时执行
  - 自动错误检测和代码修复
  - 支持复杂 NLP 任务的高效处理
  - 智能代码优化和性能调整


## 📄 许可证

本项目基于 MIT 许可证开源 - 查看 [LICENSE](LICENSE) 文件了解详情。



---

**注意**：本项目专为物流行业数据分析场景设计，使用前请确保已正确配置数据库连接和相关权限。
