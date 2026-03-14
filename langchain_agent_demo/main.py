"""
LangChain Agent Demo - 主程序入口
演示如何使用LangChain Agent系统
"""
import sys
import os
import asyncio
import logging
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import ConfigManager, AgentSystemConfig
from agents import AgentBuilder, LangChainAgent
from examples.example_tools import get_example_tools

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(char="=", length=80):
    """打印分隔线"""
    print(char * length)


def print_section(title):
    """打印章节标题"""
    print_separator()
    print(f"\n{title}\n")
    print_separator()


def setup_environment():
    """设置环境变量"""
    # 设置OpenAI API密钥（如果未设置）
    if not os.getenv("OPENAI_API_KEY"):
        print("警告: 未设置OPENAI_API_KEY环境变量")
        print("请设置环境变量: export OPENAI_API_KEY='your-api-key'")
        print("或在config/default.yaml中配置其他LLM提供者")
        print()
        
        # 为了演示，使用模拟模式
        os.environ["OPENAI_API_KEY"] = "sk-demo-key-for-testing"


def create_agent() -> LangChainAgent:
    """
    创建Agent实例
    
    Returns:
        LangChainAgent: Agent实例
    """
    print_section("创建Agent")
    
    # 加载配置
    config_manager = ConfigManager(config_dir=str(project_root / "config"))
    config = config_manager.load_config("default", "dev")
    
    print(f"Agent名称: {config.agent.name}")
    print(f"LLM提供者: {config.llm.provider}")
    print(f"LLM模型: {config.llm.model_name}")
    print(f"记忆后端: {config.memory.backend}")
    print(f"Agent类型: {config.agent.type}")
    
    # 构建Agent
    builder = AgentBuilder(config)
    agent = builder.build_agent()
    
    # 注册示例工具
    print("\n注册示例工具...")
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
        print(f"  - {tool.name}: {tool.description}")
    
    print(f"\n已注册工具: {len(agent.get_available_tools())} 个")
    print(f"已启用技能: {len(agent.get_available_skills())} 个")
    
    return agent


def demo_basic_query(agent: LangChainAgent):
    """演示基本查询功能"""
    print_section("演示1: 基本查询")
    
    questions = [
        "你好，请介绍一下你自己",
        "你能做什么？",
        "什么是LangChain？"
    ]
    
    for question in questions:
        print(f"\n问题: {question}")
        print("-" * 80)
        
        try:
            result = agent.query_sync(question, enable_deep_think=False)
            
            if result['error']:
                print(f"错误: {result['error']}")
            else:
                print(f"回答: {result['answer']}")
                
                if result['thinking']:
                    print(f"\n思考过程:")
                    print(f"  推理时间: {result['thinking'].get('reasoning_time', 0):.2f}秒")
                    print(f"  规划时间: {result['thinking'].get('planning_time', 0):.2f}秒")
        except Exception as e:
            print(f"查询失败: {e}")
        
        print()


def demo_tool_usage(agent: LangChainAgent):
    """演示工具使用"""
    print_section("演示2: 工具使用")
    
    tool_queries = [
        "计算 123 * 456 + 789",
        "现在是什么时间？",
        "帮我搜索一下人工智能的最新发展",
        "分析这段文本的字数: 这是一个测试文本，用于演示文本分析工具的功能。"
    ]
    
    for query in tool_queries:
        print(f"\n查询: {query}")
        print("-" * 80)
        
        try:
            result = agent.query_sync(query, enable_deep_think=False)
            
            if result['error']:
                print(f"错误: {result['error']}")
            else:
                print(f"回答: {result['answer']}")
                
                if result['actions']:
                    print(f"\n使用的工具:")
                    for action in result['actions']:
                        print(f"  - 工具: {action.get('tool', 'unknown')}")
                        print(f"    输入: {action.get('tool_input', {})}")
        except Exception as e:
            print(f"查询失败: {e}")
        
        print()


def demo_deep_thinking(agent: LangChainAgent):
    """演示深度思考功能"""
    print_section("演示3: 深度思考")
    
    complex_questions = [
        "如何设计一个高效的算法来解决旅行商问题？",
        "分析一下人工智能对教育行业的影响和挑战"
    ]
    
    for question in complex_questions:
        print(f"\n问题: {question}")
        print("-" * 80)
        
        try:
            result = agent.query_sync(question, enable_deep_think=True)
            
            if result['error']:
                print(f"错误: {result['error']}")
            else:
                print(f"回答: {result['answer']}")
                
                if result['thinking']:
                    print(f"\n深度思考过程:")
                    thinking = result['thinking']
                    
                    if thinking.get('reasoning'):
                        print(f"  推理结果:")
                        reasoning = thinking['reasoning']
                        if isinstance(reasoning, dict) and 'reasoning' in reasoning:
                            for step in reasoning['reasoning']:
                                print(f"    - {step}")
                    
                    if thinking.get('planning'):
                        print(f"  规划结果:")
                        planning = thinking['planning']
                        if isinstance(planning, dict) and 'output' in planning:
                            for step in planning['output']:
                                print(f"    - 步骤{step.get('step')}: {step.get('action')}")
                                print(f"      {step.get('description')}")
                    
                    print(f"\n思考耗时:")
                    print(f"  推理: {thinking.get('reasoning_time', 0):.2f}秒")
                    print(f"  规划: {thinking.get('planning_time', 0):.2f}秒")
        except Exception as e:
            print(f"查询失败: {e}")
        
        print()


def demo_conversation_memory(agent: LangChainAgent):
    """演示对话记忆功能"""
    print_section("演示4: 对话记忆")
    
    # 设置新的会话ID
    agent.set_session_id("demo_session")
    
    # 进行多轮对话
    conversation = [
        "我叫小明",
        "我的名字是什么？",
        "我喜欢编程和阅读",
        "我有什么爱好？",
        "总结一下我们的对话"
    ]
    
    for i, message in enumerate(conversation, 1):
        print(f"\n第{i}轮对话")
        print(f"用户: {message}")
        print("-" * 80)
        
        try:
            result = agent.query_sync(message, enable_deep_think=False)
            
            if result['error']:
                print(f"错误: {result['error']}")
            else:
                print(f"助手: {result['answer']}")
        except Exception as e:
            print(f"查询失败: {e}")
        
        print()
    
    # 显示对话历史
    print("\n对话历史:")
    print("-" * 80)
    history = agent.get_conversation_history()
    for msg in history:
        print(msg)
    
    print()


def demo_skill_management(agent: LangChainAgent):
    """演示技能管理"""
    print_section("演示5: 技能管理")
    
    print("当前可用的技能:")
    skills = agent.get_available_skills()
    for skill in skills:
        print(f"  - {skill}")
    
    print("\n禁用推理技能...")
    agent.disable_skill('reasoning')
    print(f"可用技能: {agent.get_available_skills()}")
    
    print("\n重新启用推理技能...")
    agent.enable_skill('reasoning')
    print(f"可用技能: {agent.get_available_skills()}")
    
    print()


def demo_tool_management(agent: LangChainAgent):
    """演示工具管理"""
    print_section("演示6: 工具管理")
    
    print("当前可用的工具:")
    tools = agent.get_available_tools()
    for tool in tools:
        print(f"  - {tool}")
    
    print("\n禁用计算器工具...")
    agent.disable_tool('calculator')
    print(f"可用工具: {agent.get_available_tools()}")
    
    print("\n重新启用计算器工具...")
    agent.enable_tool('calculator')
    print(f"可用工具: {agent.get_available_tools()}")
    
    print()


def demo_multi_session(agent: LangChainAgent):
    """演示多会话管理"""
    print_section("演示7: 多会话管理")
    
    sessions = ["session_1", "session_2", "session_3"]
    
    for session_id in sessions:
        agent.set_session_id(session_id)
        print(f"\n会话: {session_id}")
        
        # 在每个会话中发送不同的消息
        message = f"这是会话 {session_id} 的消息"
        print(f"用户: {message}")
        
        try:
            result = agent.query_sync(message, enable_deep_think=False)
            if result['error']:
                print(f"错误: {result['error']}")
            else:
                print(f"助手: {result['answer']}")
        except Exception as e:
            print(f"查询失败: {e}")
    
    print("\n所有会话:")
    all_sessions = agent.memory_manager.get_all_sessions()
    for session in all_sessions:
        print(f"  - {session}")
    
    print()


async def demo_async_query(agent: LangChainAgent):
    """演示异步查询"""
    print_section("演示8: 异步查询")
    
    questions = [
        "什么是异步编程？",
        "Python中如何使用asyncio？",
        "异步编程的优势是什么？"
    ]
    
    # 并发执行多个查询
    tasks = [agent.query(q, enable_deep_think=False) for q in questions]
    results = await asyncio.gather(*tasks)
    
    for i, (question, result) in enumerate(zip(questions, results), 1):
        print(f"\n问题{i}: {question}")
        print("-" * 80)
        
        if result['error']:
            print(f"错误: {result['error']}")
        else:
            print(f"回答: {result['answer']}")
    
    print()


def main():
    """主函数"""
    print_section("LangChain Agent Demo")
    print("这是一个高度可扩展、可配置的LangChain Agent演示系统")
    print("支持多种LLM提供者、工具、技能和记忆后端")
    
    # 设置环境
    setup_environment()
    
    # 创建Agent
    agent = create_agent()
    
    # 运行各种演示
    try:
        demo_basic_query(agent)
        demo_tool_usage(agent)
        demo_deep_thinking(agent)
        demo_conversation_memory(agent)
        demo_skill_management(agent)
        demo_tool_management(agent)
        demo_multi_session(agent)
        
        # 演示异步查询
        print_section("演示8: 异步查询")
        asyncio.run(demo_async_query(agent))
        
    except KeyboardInterrupt:
        print("\n\n用户中断程序")
    except Exception as e:
        logger.error(f"程序运行出错: {e}", exc_info=True)
    
    print_section("演示结束")
    print("感谢使用LangChain Agent Demo！")
    print()


if __name__ == "__main__":
    main()
