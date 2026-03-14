"""
LangChain Agent Demo - 个人规则管理系统
提供个人规则的创建、管理、分类和应用功能
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class RuleCategory(str, Enum):
    """规则分类枚举"""
    COMMUNICATION = "communication"  # 交流规则
    BEHAVIOR = "behavior"  # 行为规则
    KNOWLEDGE = "knowledge"  # 知识规则
    ETHICS = "ethics"  # 伦理规则
    CUSTOM = "custom"  # 自定义规则


class RulePriority(str, Enum):
    """规则优先级枚举"""
    LOW = "low"  # 低优先级
    MEDIUM = "medium"  # 中优先级
    HIGH = "high"  # 高优先级
    CRITICAL = "critical"  # 关键优先级


class PersonalRule(BaseModel):
    """个人规则模型"""
    id: str = Field(..., description="规则唯一标识")
    name: str = Field(..., description="规则名称")
    description: str = Field(..., description="规则描述")
    category: RuleCategory = Field(default=RuleCategory.CUSTOM, description="规则分类")
    priority: RulePriority = Field(default=RulePriority.MEDIUM, description="规则优先级")
    enabled: bool = Field(default=True, description="是否启用")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    tags: List[str] = Field(default_factory=list, description="规则标签")
    conditions: Dict[str, Any] = Field(default_factory=dict, description="触发条件")
    examples: List[str] = Field(default_factory=list, description="规则示例")
    
    def to_prompt(self) -> str:
        """
        将规则转换为提示词格式
        
        Returns:
            str: 提示词格式的规则
        """
        priority_prefix = {
            RulePriority.CRITICAL: "【必须】",
            RulePriority.HIGH: "【重要】",
            RulePriority.MEDIUM: "【建议】",
            RulePriority.LOW: "【可选】"
        }
        
        prompt_parts = [
            f"{priority_prefix[self.priority]} {self.name}"
        ]
        
        if self.description:
            prompt_parts.append(f"  {self.description}")
        
        if self.examples:
            prompt_parts.append("  示例:")
            for example in self.examples:
                prompt_parts.append(f"    - {example}")
        
        return "\n".join(prompt_parts)


class RuleSet(BaseModel):
    """规则集模型"""
    name: str = Field(..., description="规则集名称")
    description: str = Field(default="", description="规则集描述")
    rules: List[PersonalRule] = Field(default_factory=list, description="规则列表")
    enabled: bool = Field(default=True, description="是否启用整个规则集")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    
    def add_rule(self, rule: PersonalRule) -> None:
        """
        添加规则到规则集
        
        Args:
            rule: 规则对象
        """
        # 检查规则ID是否已存在
        rule_ids = [r.id for r in self.rules]
        if rule.id in rule_ids:
            raise ValueError(f"规则ID已存在: {rule.id}")
        
        self.rules.append(rule)
        self.updated_at = datetime.now()
        logger.info(f"规则已添加到规则集 '{self.name}': {rule.name}")
    
    def remove_rule(self, rule_id: str) -> bool:
        """
        从规则集中移除规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功移除
        """
        for i, rule in enumerate(self.rules):
            if rule.id == rule_id:
                self.rules.pop(i)
                self.updated_at = datetime.now()
                logger.info(f"规则已从规则集 '{self.name}' 中移除: {rule_id}")
                return True
        return False
    
    def get_rule(self, rule_id: str) -> Optional[PersonalRule]:
        """
        获取规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            Optional[PersonalRule]: 规则对象
        """
        for rule in self.rules:
            if rule.id == rule_id:
                return rule
        return None
    
    def enable_rule(self, rule_id: str) -> bool:
        """
        启用规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功启用
        """
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = True
            rule.updated_at = datetime.now()
            self.updated_at = datetime.now()
            logger.info(f"规则已启用: {rule.name}")
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """
        禁用规则
        
        Args:
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功禁用
        """
        rule = self.get_rule(rule_id)
        if rule:
            rule.enabled = False
            rule.updated_at = datetime.now()
            self.updated_at = datetime.now()
            logger.info(f"规则已禁用: {rule.name}")
            return True
        return False
    
    def get_enabled_rules(self) -> List[PersonalRule]:
        """
        获取所有已启用的规则
        
        Returns:
            List[PersonalRule]: 已启用的规则列表
        """
        if not self.enabled:
            return []
        
        return [rule for rule in self.rules if rule.enabled]
    
    def get_rules_by_category(self, category: RuleCategory) -> List[PersonalRule]:
        """
        按分类获取规则
        
        Args:
            category: 规则分类
        
        Returns:
            List[PersonalRule]: 规则列表
        """
        return [rule for rule in self.rules if rule.category == category]
    
    def get_rules_by_priority(self, priority: RulePriority) -> List[PersonalRule]:
        """
        按优先级获取规则
        
        Args:
            priority: 规则优先级
        
        Returns:
            List[PersonalRule]: 规则列表
        """
        return [rule for rule in self.rules if rule.priority == priority]
    
    def get_rules_by_tag(self, tag: str) -> List[PersonalRule]:
        """
        按标签获取规则
        
        Args:
            tag: 规则标签
        
        Returns:
            List[PersonalRule]: 规则列表
        """
        return [rule for rule in self.rules if tag in rule.tags]
    
    def to_prompt(self) -> str:
        """
        将规则集转换为提示词格式
        
        Returns:
            str: 提示词格式的规则集
        """
        if not self.enabled:
            return ""
        
        prompt_parts = [
            f"## {self.name}"
        ]
        
        if self.description:
            prompt_parts.append(f"{self.description}")
        
        prompt_parts.append("")
        
        enabled_rules = self.get_enabled_rules()
        if enabled_rules:
            for rule in enabled_rules:
                prompt_parts.append(rule.to_prompt())
                prompt_parts.append("")
        else:
            prompt_parts.append("（无启用的规则）")
        
        return "\n".join(prompt_parts)


class PersonalRulesManager:
    """个人规则管理器 - 管理所有个人规则和规则集"""
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        初始化个人规则管理器
        
        Args:
            storage_path: 规则存储路径（JSON文件）
        """
        self.storage_path = storage_path
        self._rule_sets: Dict[str, RuleSet] = {}
        self._default_rules: List[PersonalRule] = []
        
        if storage_path:
            self._load_from_storage()
        else:
            self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """初始化默认规则"""
        default_rules = [
            PersonalRule(
                id="rule_001",
                name="友好交流",
                description="始终保持友好、礼貌和尊重的态度与用户交流",
                category=RuleCategory.COMMUNICATION,
                priority=RulePriority.HIGH,
                tags=["交流", "礼貌"]
            ),
            PersonalRule(
                id="rule_002",
                name="诚实回答",
                description="如果不确定答案，诚实地说明而不是编造信息",
                category=RuleCategory.ETHICS,
                priority=RulePriority.CRITICAL,
                tags=["诚实", "准确"]
            ),
            PersonalRule(
                id="rule_003",
                name="保护隐私",
                description="不要询问或存储用户的敏感个人信息",
                category=RuleCategory.ETHICS,
                priority=RulePriority.CRITICAL,
                tags=["隐私", "安全"]
            ),
            PersonalRule(
                id="rule_004",
                name="清晰表达",
                description="使用简洁、清晰、易懂的语言回答问题",
                category=RuleCategory.COMMUNICATION,
                priority=RulePriority.MEDIUM,
                tags=["表达", "清晰"]
            ),
            PersonalRule(
                id="rule_005",
                name="主动帮助",
                description="在用户需要时主动提供帮助和建议",
                category=RuleCategory.BEHAVIOR,
                priority=RulePriority.MEDIUM,
                tags=["帮助", "主动"]
            )
        ]
        
        self._default_rules = default_rules
        
        # 创建默认规则集
        default_rule_set = RuleSet(
            name="默认规则集",
            description="系统默认的个人规则",
            rules=default_rules
        )
        
        self._rule_sets["default"] = default_rule_set
        logger.info("默认规则已初始化")
    
    def _load_from_storage(self) -> None:
        """从存储加载规则"""
        try:
            path = Path(self.storage_path)
            if not path.exists():
                self._initialize_default_rules()
                return
            
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 加载规则集
            for set_data in data.get('rule_sets', []):
                # 转换datetime字符串为datetime对象
                if 'created_at' in set_data and isinstance(set_data['created_at'], str):
                    set_data['created_at'] = datetime.fromisoformat(set_data['created_at'])
                if 'updated_at' in set_data and isinstance(set_data['updated_at'], str):
                    set_data['updated_at'] = datetime.fromisoformat(set_data['updated_at'])
                
                # 转换规则中的datetime
                for rule_dict in set_data.get('rules', []):
                    if 'created_at' in rule_dict and isinstance(rule_dict['created_at'], str):
                        rule_dict['created_at'] = datetime.fromisoformat(rule_dict['created_at'])
                    if 'updated_at' in rule_dict and isinstance(rule_dict['updated_at'], str):
                        rule_dict['updated_at'] = datetime.fromisoformat(rule_dict['updated_at'])
                
                rule_set = RuleSet(**set_data)
                self._rule_sets[rule_set.name] = rule_set
            
            logger.info(f"规则已从存储加载: {self.storage_path}")
        
        except Exception as e:
            logger.error(f"加载规则失败: {e}")
            self._initialize_default_rules()
    
    def _save_to_storage(self) -> None:
        """保存规则到存储"""
        if not self.storage_path:
            return
        
        try:
            path = Path(self.storage_path)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # 转换datetime为字符串
            rule_sets_data = []
            for rule_set in self._rule_sets.values():
                rule_set_dict = rule_set.dict()
                
                # 转换规则中的datetime
                for rule_dict in rule_set_dict['rules']:
                    if 'created_at' in rule_dict and rule_dict['created_at']:
                        rule_dict['created_at'] = rule_dict['created_at'].isoformat()
                    if 'updated_at' in rule_dict and rule_dict['updated_at']:
                        rule_dict['updated_at'] = rule_dict['updated_at'].isoformat()
                
                # 转换规则集中的datetime
                if 'created_at' in rule_set_dict and rule_set_dict['created_at']:
                    rule_set_dict['created_at'] = rule_set_dict['created_at'].isoformat()
                if 'updated_at' in rule_set_dict and rule_set_dict['updated_at']:
                    rule_set_dict['updated_at'] = rule_set_dict['updated_at'].isoformat()
                
                rule_sets_data.append(rule_set_dict)
            
            data = {
                'rule_sets': rule_sets_data
            }
            
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"规则已保存到存储: {self.storage_path}")
        
        except Exception as e:
            logger.error(f"保存规则失败: {e}")
    
    def create_rule_set(
        self,
        name: str,
        description: str = ""
    ) -> RuleSet:
        """
        创建规则集
        
        Args:
            name: 规则集名称
            description: 规则集描述
        
        Returns:
            RuleSet: 规则集对象
        """
        if name in self._rule_sets:
            raise ValueError(f"规则集已存在: {name}")
        
        rule_set = RuleSet(name=name, description=description)
        self._rule_sets[name] = rule_set
        
        self._save_to_storage()
        logger.info(f"规则集已创建: {name}")
        
        return rule_set
    
    def get_rule_set(self, name: str) -> Optional[RuleSet]:
        """
        获取规则集
        
        Args:
            name: 规则集名称
        
        Returns:
            Optional[RuleSet]: 规则集对象
        """
        return self._rule_sets.get(name)
    
    def list_rule_sets(self) -> List[str]:
        """
        列出所有规则集
        
        Returns:
            List[str]: 规则集名称列表
        """
        return list(self._rule_sets.keys())
    
    def delete_rule_set(self, name: str) -> bool:
        """
        删除规则集
        
        Args:
            name: 规则集名称
        
        Returns:
            bool: 是否成功删除
        """
        if name in self._rule_sets:
            del self._rule_sets[name]
            self._save_to_storage()
            logger.info(f"规则集已删除: {name}")
            return True
        return False
    
    def add_rule(
        self,
        rule_set_name: str,
        rule: PersonalRule
    ) -> None:
        """
        添加规则到规则集
        
        Args:
            rule_set_name: 规则集名称
            rule: 规则对象
        """
        rule_set = self.get_rule_set(rule_set_name)
        if not rule_set:
            raise ValueError(f"规则集不存在: {rule_set_name}")
        
        rule_set.add_rule(rule)
        self._save_to_storage()
    
    def remove_rule(
        self,
        rule_set_name: str,
        rule_id: str
    ) -> bool:
        """
        从规则集移除规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功移除
        """
        rule_set = self.get_rule_set(rule_set_name)
        if not rule_set:
            return False
        
        result = rule_set.remove_rule(rule_id)
        if result:
            self._save_to_storage()
        
        return result
    
    def get_rule(
        self,
        rule_set_name: str,
        rule_id: str
    ) -> Optional[PersonalRule]:
        """
        获取规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
        
        Returns:
            Optional[PersonalRule]: 规则对象
        """
        rule_set = self.get_rule_set(rule_set_name)
        if not rule_set:
            return None
        
        return rule_set.get_rule(rule_id)
    
    def enable_rule(
        self,
        rule_set_name: str,
        rule_id: str
    ) -> bool:
        """
        启用规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功启用
        """
        rule_set = self.get_rule_set(rule_set_name)
        if not rule_set:
            return False
        
        result = rule_set.enable_rule(rule_id)
        if result:
            self._save_to_storage()
        
        return result
    
    def disable_rule(
        self,
        rule_set_name: str,
        rule_id: str
    ) -> bool:
        """
        禁用规则
        
        Args:
            rule_set_name: 规则集名称
            rule_id: 规则ID
        
        Returns:
            bool: 是否成功禁用
        """
        rule_set = self.get_rule_set(rule_set_name)
        if not rule_set:
            return False
        
        result = rule_set.disable_rule(rule_id)
        if result:
            self._save_to_storage()
        
        return result
    
    def get_all_enabled_rules(self) -> List[PersonalRule]:
        """
        获取所有已启用的规则
        
        Returns:
            List[PersonalRule]: 已启用的规则列表
        """
        enabled_rules = []
        
        for rule_set in self._rule_sets.values():
            enabled_rules.extend(rule_set.get_enabled_rules())
        
        # 按优先级排序
        priority_order = {
            RulePriority.CRITICAL: 0,
            RulePriority.HIGH: 1,
            RulePriority.MEDIUM: 2,
            RulePriority.LOW: 3
        }
        
        enabled_rules.sort(key=lambda r: priority_order[r.priority])
        
        return enabled_rules
    
    def to_prompt(self) -> str:
        """
        将所有规则转换为提示词格式
        
        Returns:
            str: 提示词格式的规则
        """
        prompt_parts = ["# 个人规则"]
        prompt_parts.append("")
        
        enabled_rules = self.get_all_enabled_rules()
        
        if enabled_rules:
            # 按分类分组
            rules_by_category = {}
            for rule in enabled_rules:
                if rule.category not in rules_by_category:
                    rules_by_category[rule.category] = []
                rules_by_category[rule.category].append(rule)
            
            # 生成提示词
            for category, rules in rules_by_category.items():
                category_name = {
                    RuleCategory.COMMUNICATION: "交流规则",
                    RuleCategory.BEHAVIOR: "行为规则",
                    RuleCategory.KNOWLEDGE: "知识规则",
                    RuleCategory.ETHICS: "伦理规则",
                    RuleCategory.CUSTOM: "自定义规则"
                }.get(category, category.value)
                
                prompt_parts.append(f"## {category_name}")
                prompt_parts.append("")
                
                for rule in rules:
                    prompt_parts.append(rule.to_prompt())
                    prompt_parts.append("")
        else:
            prompt_parts.append("（无启用的个人规则）")
        
        return "\n".join(prompt_parts)
    
    def import_rules(
        self,
        rules_data: Dict[str, Any]
    ) -> None:
        """
        导入规则
        
        Args:
            rules_data: 规则数据
        """
        for set_data in rules_data.get('rule_sets', []):
            rule_set = RuleSet(**set_data)
            self._rule_sets[rule_set.name] = rule_set
        
        self._save_to_storage()
        logger.info("规则已导入")
    
    def export_rules(self) -> Dict[str, Any]:
        """
        导出规则
        
        Returns:
            Dict[str, Any]: 规则数据
        """
        return {
            'rule_sets': [
                rule_set.dict()
                for rule_set in self._rule_sets.values()
            ]
        }
    
    def search_rules(
        self,
        keyword: str,
        category: Optional[RuleCategory] = None
    ) -> List[PersonalRule]:
        """
        搜索规则
        
        Args:
            keyword: 搜索关键词
            category: 规则分类（可选）
        
        Returns:
            List[PersonalRule]: 匹配的规则列表
        """
        results = []
        
        for rule_set in self._rule_sets.values():
            for rule in rule_set.rules:
                # 检查分类
                if category and rule.category != category:
                    continue
                
                # 检查关键词
                keyword_lower = keyword.lower()
                if (keyword_lower in rule.name.lower() or
                    keyword_lower in rule.description.lower() or
                    any(keyword_lower in tag.lower() for tag in rule.tags)):
                    results.append(rule)
        
        return results
