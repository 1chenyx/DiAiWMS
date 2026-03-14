"""
LangChain Agent Demo - 个人规则功能演示
展示如何使用个人规则管理系统
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core import ConfigManager, RuleCategory, RulePriority
from agents import AgentBuilder
from examples.example_tools import get_example_tools


def print_separator(char="=", length=80):
    """打印分隔线"""
    print(char * length)


def print_section(title):
    """打印章节标题"""
    print_separator()
    print(f"\n{title}\n")
    print_separator()


def demo_personal_rules():
    """演示个人规则功能"""
    print_section("个人规则功能演示")
    
    # 1. 创建Agent
    print("1. 创建Agent...")
    config_manager = ConfigManager(config_dir=str(project_root / "config"))
    config = config_manager.load_config("default")
    
    builder = AgentBuilder(config)
    builder.build_llm_provider()
    builder.build_tool_manager()
    builder.build_skill_manager()
    builder.build_memory_manager()
    builder.build_thinker()
    
    # 创建个人规则管理器（带存储）
    rules_storage_path = str(project_root / "data" / "personal_rules.json")
    builder.build_personal_rules_manager(rules_storage_path)
    
    agent = builder.build_agent()
    
    # 注册工具
    print("2. 注册示例工具...")
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
    
    # 3. 查看默认规则
    print_section("3. 查看默认规则")
    rule_sets = agent.list_rule_sets()
    print(f"规则集列表: {rule_sets}\n")
    
    default_rules = agent.list_personal_rules("default")
    print("默认规则集内容:")
    for rule in default_rules:
        print(f"  - [{rule['priority']}] {rule['name']}")
        print(f"    {rule['description']}")
        print(f"    标签: {', '.join(rule['tags'])}")
        print()
    
    # 4. 创建自定义规则集
    print_section("4. 创建自定义规则集")
    agent.create_rule_set(
        name="工作规则",
        description="用于工作场景的个人规则"
    )
    print("已创建规则集: 工作规则\n")
    
    # 5. 添加个人规则
    print_section("5. 添加个人规则")
    
    # 添加工作相关规则
    agent.add_personal_rule(
        rule_set_name="工作规则",
        rule_id="work_001",
        name="专业表达",
        description="在工作场景中使用专业、正式的语言表达",
        category="communication",
        priority="high",
        tags=["工作", "专业", "表达"],
        examples=[
            "用户: 帮我写个邮件",
            "助手: 好的，我来帮您撰写一封专业的商务邮件..."
        ]
    )
    print("已添加规则: 专业表达")
    
    agent.add_personal_rule(
        rule_set_name="工作规则",
        rule_id="work_002",
        name="数据保密",
        description="严格保护工作相关的敏感数据和信息",
        category="ethics",
        priority="critical",
        tags=["工作", "保密", "安全"],
        examples=[
            "用户: 帮我分析这个客户数据",
            "助手: 我会严格保护数据隐私，仅进行必要的分析..."
        ]
    )
    print("已添加规则: 数据保密")
    
    agent.add_personal_rule(
        rule_set_name="工作规则",
        rule_id="work_003",
        name="效率优先",
        description="在工作场景中优先考虑效率和结果",
        category="behavior",
        priority="medium",
        tags=["工作", "效率"]
    )
    print("已添加规则: 效率优先\n")
    
    # 6. 创建学习规则集
    print_section("6. 创建学习规则集")
    agent.create_rule_set(
        name="学习规则",
        description="用于学习场景的个人规则"
    )
    
    agent.add_personal_rule(
        rule_set_name="学习规则",
        rule_id="study_001",
        name="循序渐进",
        description="在学习过程中按照循序渐进的方式讲解，确保理解",
        category="behavior",
        priority="high",
        tags=["学习", "教学"],
        examples=[
            "用户: 教我Python编程",
            "助手: 我们从最基础的概念开始，逐步深入..."
        ]
    )
    print("已添加规则: 循序渐进")
    
    agent.add_personal_rule(
        rule_set_name="学习规则",
        rule_id="study_002",
        name="鼓励探索",
        description="鼓励用户主动探索和实践",
        category="behavior",
        priority="medium",
        tags=["学习", "探索"]
    )
    print("已添加规则: 鼓励探索\n")
    
    # 7. 列出所有规则集
    print_section("7. 列出所有规则集")
    rule_sets = agent.list_rule_sets()
    print(f"规则集列表: {rule_sets}\n")
    
    for set_name in rule_sets:
        rules = agent.list_personal_rules(set_name)
        print(f"规则集: {set_name}")
        for rule in rules:
            status = "启用" if rule['enabled'] else "禁用"
            print(f"  - [{status}] [{rule['priority']}] {rule['name']}")
        print()
    
    # 8. 搜索规则
    print_section("8. 搜索规则")
    
    # 按关键词搜索
    results = agent.search_personal_rules("工作")
    print(f"搜索关键词 '工作' 的结果:")
    for rule in results:
        print(f"  - {rule['name']} (规则集: {rule.get('rule_set', 'unknown')})")
    print()
    
    # 按分类搜索
    results = agent.search_personal_rules("", category="ethics")
    print(f"搜索分类 'ethics' 的结果:")
    for rule in results:
        print(f"  - [{rule['priority']}] {rule['name']}")
    print()
    
    # 9. 禁用和启用规则
    print_section("9. 禁用和启用规则")
    
    # 禁用默认规则中的"友好交流"
    agent.disable_personal_rule("default", "rule_001")
    print("已禁用规则: 友好交流")
    
    # 启用工作规则集中的"效率优先"
    agent.enable_personal_rule("工作规则", "work_003")
    print("已启用规则: 效率优先\n")
    
    # 查看启用状态
    enabled_rules = agent.list_personal_rules()
    print(f"当前启用的规则数量: {len(enabled_rules)}")
    for rule in enabled_rules[:5]:  # 只显示前5个
        print(f"  - [{rule['priority']}] {rule['name']}")
    print()
    
    # 10. 查看规则提示词
    print_section("10. 查看规则提示词")
    rules_prompt = agent.get_personal_rules_prompt()
    print(rules_prompt)
    print()
    
    # 11. 导出规则
    print_section("11. 导出规则")
    rules_data = agent.export_personal_rules()
    print(f"导出的规则数据:")
    print(f"  规则集数量: {len(rules_data['rule_sets'])}")
    for rule_set in rules_data['rule_sets']:
        print(f"  - {rule_set['name']}: {len(rule_set['rules'])} 条规则")
    print()
    
    # 12. 测试规则应用
    print_section("12. 测试规则应用")
    print("注意: 由于需要真实的LLM API，这里仅展示规则已集成到Agent中\n")
    
    print("当前系统提示词包含:")
    print("  - 角色设定")
    print("  - 个人规则（按优先级排序）")
    print("  - 系统规则")
    print("  - 约束")
    print("  - 能力")
    print("  - 自定义指令")
    print()
    
    # 13. 删除规则
    print_section("13. 删除规则")
    
    # 删除学习规则集
    agent.delete_rule_set("学习规则")
    print("已删除规则集: 学习规则")
    
    # 删除工作规则集中的某条规则
    agent.remove_personal_rule("工作规则", "work_003")
    print("已删除规则: 效率优先\n")
    
    # 查看剩余规则集
    rule_sets = agent.list_rule_sets()
    print(f"剩余规则集: {rule_sets}\n")
    
    print_section("演示完成")
    print("个人规则功能已成功演示！")
    print(f"规则数据已保存到: {rules_storage_path}")
    print()


if __name__ == "__main__":
    demo_personal_rules()
