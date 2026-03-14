# LangChain Agent Demo 快速开始指南

这是一个快速开始指南，帮助你快速上手LangChain Agent Demo系统。

## 安装步骤

### 1. 克隆或下载项目

```bash
cd langchain_agent_demo
```

### 2. 创建虚拟环境（推荐）

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置API密钥

#### 使用OpenAI（推荐）

```bash
# Windows
set OPENAI_API_KEY=your-api-key-here

# Linux/Mac
export OPENAI_API_KEY='your-api-key-here'
```

#### 或使用其他LLM提供者

编辑 `config/default.yaml` 文件，修改 `llm` 部分：

```yaml
llm:
  provider: ollama  # 使用本地Ollama
  model_name: llama2
  api_base: http://localhost:11434
```

## 运行演示

```bash
python main.py
```

## 常见问题

### Q: 提示API密钥错误

**A:** 确保已正确设置环境变量：
```bash
echo $OPENAI_API_KEY  # Linux/Mac
echo %OPENAI_API_KEY%  # Windows
```

### Q: 想使用本地模型

**A:** 安装Ollama并修改配置：
```bash
# 安装Ollama
# https://ollama.ai/

# 下载模型
ollama pull llama2

# 修改config/default.yaml
llm:
  provider: ollama
  model_name: llama2
```

### Q: 如何添加自定义工具

**A:** 参考 `examples/custom_tools.py`，创建工具类并使用 `@tool_metadata` 装饰器。

### Q: 如何修改Agent的行为

**A:** 编辑 `config/default.yaml` 中的 `system_prompt` 部分，自定义角色、规则和约束。

### Q: 记忆存储在哪里

**A:** 默认使用内存存储。如需持久化，修改配置：
```yaml
memory:
  backend: sqlite  # 或 redis
  sqlite_path: "memory.db"
```

## 下一步

- 阅读 [README.md](README.md) 了解详细功能
- 查看 `examples/` 目录中的示例代码
- 修改 `config/default.yaml` 自定义配置
- 创建自己的工具和技能

## 获取帮助

如有问题，请查看：
- LangChain官方文档: https://python.langchain.com
- 项目README: [README.md](README.md)
