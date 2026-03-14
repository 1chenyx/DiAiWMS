"""
个人规则功能简化演示 - 不依赖LangChain
展示个人规则管理系统的核心功能
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.personal_rules import (
    RuleCategory,
    RulePriority,
    PersonalRule,
    RuleSet,
    PersonalRulesManager
)


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
    
    # 1. 创建规则管理器
    print("1. 创建个人规则管理器...")
    rules_storage_path = str(project_root / "data" / "personal_rules.json")
    manager = PersonalRulesManager(rules_storage_path)
    print(f"   规则存储路径: {rules_storage_path}\n")
    
    # 2. 查看默认规则
    print_section("2. 查看默认规则")
    rule_sets = manager.list_rule_sets()
    print(f"规则集列表: {rule_sets}\n")
    
    default_rule_set = manager.get_rule_set("default")
    if default_rule_set:
        print("默认规则集内容:")
        for rule in default_rule_set.rules:
            status = "启用" if rule.enabled else "禁用"
            print(f"  - [{status}] [{rule.priority.value}] {rule.name}")
            print(f"    {rule.description}")
            print(f"    标签: {', '.join(rule.tags)}")
            print()
    
    # 3. 创建自定义规则集
    print_section("3. 创建自定义规则集")
    
    # 创建工作规则集
    work_rule_set = manager.create_rule_set(
        name="工作规则",
        description="用于工作场景的个人规则"
    )
    print("已创建规则集: 工作规则\n")
    
    # 创建学习规则集
    study_rule_set = manager.create_rule_set(
        name="学习规则",
        description="用于学习场景的个人规则"
    )
    print("已创建规则集: 学习规则\n")
    
    # 4. 添加个人规则
    print_section("4. 添加个人规则")
    
    # 添加工作相关规则
    work_rules = [
        PersonalRule(
            id="work_001",
            name="专业表达",
            description="在工作场景中使用专业、正式的语言表达",
            category=RuleCategory.COMMUNICATION,
            priority=RulePriority.HIGH,
            tags=["工作", "专业", "表达"],
            examples=[
                "用户: 帮我写个邮件",
                "助手: 好的，我来帮您撰写一封专业的商务邮件..."
            ]
        ),
        PersonalRule(
            id="work_002",
            name="数据保密",
            description="严格保护工作相关的敏感数据和信息",
            category=RuleCategory.ETHICS,
            priority=RulePriority.CRITICAL,
            tags=["工作", "保密", "安全"],
            examples=[
                "用户: 帮我分析这个客户数据",
                "助手: 我会严格保护数据隐私，仅进行必要的分析..."
            ]
        ),
        PersonalRule(
            id="work_003",
            name="效率优先",
            description="在工作场景中优先考虑效率和结果",
            category=RuleCategory.BEHAVIOR,
            priority=RulePriority.MEDIUM,
            tags=["工作", "效率"]
        )
    ]
    
    for rule in work_rules:
        manager.add_rule("工作规则", rule)
        print(f"已添加规则: {rule.name}")
    
    print()
    
    # 添加学习相关规则
    study_rules = [
        PersonalRule(
            id="study_001",
            name="循序渐进",
            description="在学习过程中按照循序渐进的方式讲解，确保理解",
            category=RuleCategory.BEHAVIOR,
            priority=RulePriority.HIGH,
            tags=["学习", "教学"],
            examples=[
                "用户: 教我Python编程",
                "助手: 我们从最基础的概念开始，逐步深入..."
            ]
        ),
        PersonalRule(
            id="study_002",
            name="鼓励探索",
            description="鼓励用户主动探索和实践",
            category=RuleCategory.BEHAVIOR,
            priority=RulePriority.MEDIUM,
            tags=["学习", "探索"]
        )
    ]
    
    for rule in study_rules:
        manager.add_rule("学习规则", rule)
        print(f"已添加规则: {rule.name}")
    
    print()
    
    # 5. 列出所有规则集
    print_section("5. 列出所有规则集")
    rule_sets = manager.list_rule_sets()
    print(f"规则集列表: {rule_sets}\n")
    
    for set_name in rule_sets:
        rule_set = manager.get_rule_set(set_name)
        if rule_set:
            print(f"规则集: {set_name}")
            if rule_set.description:
                print(f"  描述: {rule_set.description}")
            print(f"  规则数量: {len(rule_set.rules)}")
            print(f"  启用状态: {'启用' if rule_set.enabled else '禁用'}")
            print()
    
    # 6. 搜索规则
    print_section("6. 搜索规则")
    
    # 按关键词搜索
    results = manager.search_rules("工作")
    print(f"搜索关键词 '工作' 的结果:")
    for rule in results:
        print(f"  - {rule.name} (规则集: {rule.id[:rule.id.rfind('_')]})")
    print()
    
    # 按分类搜索
    results = manager.search_rules("", category=RuleCategory.ETHICS)
    print(f"搜索分类 'ethics' 的结果:")
    for rule in results:
        print(f"  - [{rule.priority.value}] {rule.name}")
    print()
    
    # 7. 禁用和启用规则
    print_section("7. 禁用和启用规则")
    
    # 禁用默认规则中的"友好交流"
    manager.disable_rule("default", "rule_001")
    print("已禁用规则: 友好交流")
    
    # 启用工作规则集中的"效率优先"
    manager.enable_rule("工作规则", "work_003")
    print("已启用规则: 效率优先\n")
    
    # 查看启用状态
    enabled_rules = manager.get_all_enabled_rules()
    print(f"当前启用的规则数量: {len(enabled_rules)}")
    print("启用的规则（前10个）:")
    for i, rule in enumerate(enabled_rules[:10], 1):
        print(f"  {i}. [{rule.priority.value}] {rule.name}")
    print()
    
    # 8. 查看规则提示词
    print_section("8. 查看规则提示词")
    rules_prompt = manager.to_prompt()
    print(rules_prompt)
    print()
    
    # 9. 导出规则
    print_section("9. 导出规则")
    rules_data = manager.export_rules()
    print(f"导出的规则数据:")
    print(f"  规则集数量: {len(rules_data['rule_sets'])}")
    for rule_set in rules_data['rule_sets']:
        print(f"  - {rule_set['name']}: {len(rule_set['rules'])} 条规则")
    print()
    
    # 10. 删除规则
    print_section("10. 删除规则")
    
    # 删除学习规则集
    manager.delete_rule_set("学习规则")
    print("已删除规则集: 学习规则")
    
    # 删除工作规则集中的某条规则
    manager.remove_rule("工作规则", "work_003")
    print("已删除规则: 效率优先\n")
    
    # 查看剩余规则集
    rule_sets = manager.list_rule_sets()
    print(f"剩余规则集: {rule_sets}\n")
    
    # 11. 按分类查看规则
    print_section("11. 按分类查看规则")
    
    categories = [
        RuleCategory.COMMUNICATION,
        RuleCategory.BEHAVIOR,
        RuleCategory.ETHICS
    ]
    
    for category in categories:
        category_name = {
            RuleCategory.COMMUNICATION: "交流规则",
            RuleCategory.BEHAVIOR: "行为规则",
            RuleCategory.ETHICS: "伦理规则"
        }.get(category, category.value)
        
        all_rules = []
        for rule_set in manager._rule_sets.values():
            all_rules.extend(rule_set.get_rules_by_category(category))
        
        if all_rules:
            print(f"{category_name}:")
            for rule in all_rules:
                status = "启用" if rule.enabled else "禁用"
                print(f"  - [{status}] {rule.name}")
            print()
    
    # 12. 按优先级查看规则
    print_section("12. 按优先级查看规则")
    
    priorities = [
        RulePriority.CRITICAL,
        RulePriority.HIGH,
        RulePriority.MEDIUM,
        RulePriority.LOW
    ]
    
    for priority in priorities:
        all_rules = []
        for rule_set in manager._rule_sets.values():
            all_rules.extend(rule_set.get_rules_by_priority(priority))
        
        if all_rules:
            print(f"{priority.value.upper()} 优先级规则:")
            for rule in all_rules:
                status = "启用" if rule.enabled else "禁用"
                print(f"  - [{status}] {rule.name}")
            print()
    
    # 13. 按标签查看规则
    print_section("13. 按标签查看规则")
    
    work_rule_set = manager.get_rule_set("工作规则")
    if work_rule_set:
        tags = set()
        for rule in work_rule_set.rules:
            tags.update(rule.tags)
        
        print("工作规则集中的标签:")
        for tag in sorted(tags):
            rules = work_rule_set.get_rules_by_tag(tag)
            print(f"  标签 '{tag}': {len(rules)} 条规则")
            for rule in rules:
                print(f"    - {rule.name}")
        print()
    
    # 14. 查看规则详情
    print_section("14. 查看规则详情")
    
    rule = manager.get_rule("工作规则", "work_001")
    if rule:
        print("规则详情:")
        print(f"  ID: {rule.id}")
        print(f"  名称: {rule.name}")
        print(f"  描述: {rule.description}")
        print(f"  分类: {rule.category.value}")
        print(f"  优先级: {rule.priority.value}")
        print(f"  启用状态: {'启用' if rule.enabled else '禁用'}")
        print(f"  创建时间: {rule.created_at}")
        print(f"  更新时间: {rule.updated_at}")
        print(f"  标签: {', '.join(rule.tags)}")
        print(f"  示例数量: {len(rule.examples)}")
        if rule.examples:
            print("  示例:")
            for example in rule.examples:
                print(f"    - {example}")
        print()
    
    # 15. 查看规则集提示词
    print_section("15. 查看规则集提示词")
    
    work_rule_set = manager.get_rule_set("工作规则")
    if work_rule_set:
        print("工作规则集的提示词:")
        print(work_rule_set.to_prompt())
        print()
    
    print_section("演示完成")
    print("个人规则功能已成功演示！")
    print(f"规则数据已保存到: {rules_storage_path}")
    print("\n主要功能:")
    print("  ✓ 规则集管理（创建、删除、列表）")
    print("  ✓ 个人规则管理（添加、删除、启用、禁用）")
    print("  ✓ 规则搜索（按关键词、分类、标签）")
    print("  ✓ 规则优先级管理")
    print("  ✓ 规则提示词生成")
    print("  ✓ 规则导入导出")
    print("  ✓ 规则持久化存储")
    print()


if __name__ == "__main__":
    demo_personal_rules()
