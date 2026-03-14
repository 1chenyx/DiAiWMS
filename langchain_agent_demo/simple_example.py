"""
简单的使用示例 - 展示如何快速使用LangChain Agent系统
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import ConfigManager
from agents import AgentBuilder
from examples.example_tools import get_example_tools


def simple_example():
    """简单使用示例"""
    print("=== 简单使用示例 ===\n")
    
    # 1. 加载配置
    print("1. 加载配置...")
    config_manager = ConfigManager(config_dir=str(project_root / "config"))
    config = config_manager.load_config("default")
    print(f"   Agent名称: {config.agent.name}\n")
    
    # 2. 构建Agent
    print("2. 构建Agent...")
    builder = AgentBuilder(config)
    agent = builder.build_agent()
    print(f"   Agent已创建\n")
    
    # 3. 注册工具
    print("3. 注册示例工具...")
    example_tools = get_example_tools()
    for tool in example_tools:
        agent.tool_manager.register_tool(
            tool,
            agent.tool_manager.registry.ToolMetadata(
                name=tool.name,
                description=tool.description,
                version="1.0.0",
                category="example"
            )
        )
    print(f"   已注册 {len(example_tools)} 个工具\n")
    
    # 4. 进行查询
    print("4. 开始查询...\n")
    
    questions = [
        "你好",
        "计算 25 * 4",
        "现在是什么时间？"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"问题{i}: {question}")
        print("-" * 50)
        
        try:
            result = agent.query_sync(question, enable_deep_think=False)
            
            if result['error']:
                print(f"错误: {result['error']}")
            else:
                print(f"回答: {result['answer']}")
        except Exception as e:
            print(f"查询失败: {e}")
        
        print()
    
    print("=== 示例完成 ===")


if __name__ == "__main__":
    simple_example()
