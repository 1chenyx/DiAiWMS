"""
LangChain Agent Demo - 示例工具
提供一些实用的工具示例，包括计算器、搜索、日期时间等
"""
from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import math
import datetime
import re
import logging

logger = logging.getLogger(__name__)


class CalculatorInput(BaseModel):
    """计算器输入模型"""
    expression: str = Field(description="要计算的数学表达式，例如: 2 + 3 * 4")


class CalculatorTool(BaseTool):
    """计算器工具 - 执行数学计算"""
    
    name = "calculator"
    description = "执行数学计算，支持加减乘除、幂运算、三角函数等"
    args_schema: Type[BaseModel] = CalculatorInput
    
    def _run(self, expression: str) -> str:
        """
        执行计算
        
        Args:
            expression: 数学表达式
        
        Returns:
            str: 计算结果
        """
        try:
            # 安全的数学计算
            allowed_names = {
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                'pow': pow,
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'pi': math.pi,
                'e': math.e
            }
            
            # 使用eval进行计算，但限制可用的函数
            result = eval(expression, {"__builtins__": {}}, allowed_names)
            
            return f"计算结果: {result}"
        
        except Exception as e:
            return f"计算错误: {str(e)}"
    
    async def _arun(self, expression: str) -> str:
        """异步执行计算"""
        return self._run(expression)


class SearchInput(BaseModel):
    """搜索输入模型"""
    query: str = Field(description="搜索查询字符串")
    max_results: int = Field(default=5, description="返回的最大结果数")


class SearchTool(BaseTool):
    """搜索工具 - 模拟信息搜索"""
    
    name = "search"
    description = "搜索信息，返回相关结果"
    args_schema: Type[BaseModel] = SearchInput
    
    def _run(self, query: str, max_results: int = 5) -> str:
        """
        执行搜索
        
        Args:
            query: 搜索查询
            max_results: 最大结果数
        
        Returns:
            str: 搜索结果
        """
        try:
            # 模拟搜索结果
            # 在实际应用中，这里会调用真实的搜索API
            results = []
            
            # 生成一些模拟结果
            for i in range(min(max_results, 3)):
                results.append({
                    'title': f"关于 '{query}' 的搜索结果 {i+1}",
                    'snippet': f"这是关于 '{query}' 的第 {i+1} 个搜索结果的摘要信息...",
                    'url': f"https://example.com/search?q={query}&result={i+1}"
                })
            
            # 格式化结果
            formatted_results = []
            for i, result in enumerate(results, 1):
                formatted_results.append(
                    f"{i}. {result['title']}\n"
                    f"   {result['snippet']}\n"
                    f"   {result['url']}"
                )
            
            return "搜索结果:\n" + "\n\n".join(formatted_results)
        
        except Exception as e:
            return f"搜索错误: {str(e)}"
    
    async def _arun(self, query: str, max_results: int = 5) -> str:
        """异步执行搜索"""
        return self._run(query, max_results)


class DateTimeInput(BaseModel):
    """日期时间输入模型"""
    operation: str = Field(description="操作类型: 'current' 获取当前时间, 'format' 格式化时间")
    format: str = Field(default="%Y-%m-%d %H:%M:%S", description="时间格式字符串")


class DateTimeTool(BaseTool):
    """日期时间工具 - 获取和格式化日期时间"""
    
    name = "datetime"
    description = "获取当前日期时间或格式化时间"
    args_schema: Type[BaseModel] = DateTimeInput
    
    def _run(self, operation: str = "current", format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """
        执行日期时间操作
        
        Args:
            operation: 操作类型
            format: 时间格式
        
        Returns:
            str: 日期时间结果
        """
        try:
            now = datetime.datetime.now()
            
            if operation == "current":
                return f"当前时间: {now.strftime(format)}"
            elif operation == "format":
                return f"格式化时间: {now.strftime(format)}"
            else:
                return f"当前时间: {now.strftime(format)}"
        
        except Exception as e:
            return f"日期时间错误: {str(e)}"
    
    async def _arun(self, operation: str = "current", format: str = "%Y-%m-%d %H:%M:%S") -> str:
        """异步执行日期时间操作"""
        return self._run(operation, format)


class CodeExecutorInput(BaseModel):
    """代码执行器输入模型"""
    code: str = Field(description="要执行的Python代码")
    timeout: int = Field(default=30, description="执行超时时间（秒）")


class CodeExecutorTool(BaseTool):
    """代码执行器工具 - 执行Python代码"""
    
    name = "code_executor"
    description = "执行Python代码并返回结果"
    args_schema: Type[BaseModel] = CodeExecutorInput
    
    def _run(self, code: str, timeout: int = 30) -> str:
        """
        执行Python代码
        
        Args:
            code: Python代码
            timeout: 超时时间
        
        Returns:
            str: 执行结果
        """
        try:
            # 准备执行环境
            import sys
            from io import StringIO
            
            # 捕获输出
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            try:
                # 执行代码
                exec_globals = {
                    '__builtins__': {
                        'print': print,
                        'len': len,
                        'range': range,
                        'int': int,
                        'float': float,
                        'str': str,
                        'list': list,
                        'dict': dict,
                        'set': set,
                        'tuple': tuple,
                        'sum': sum,
                        'max': max,
                        'min': min,
                        'abs': abs,
                        'round': round,
                    }
                }
                
                exec(code, exec_globals)
                
                # 获取输出
                output = captured_output.getvalue()
                
                if output:
                    return f"执行输出:\n{output}"
                else:
                    return "代码执行成功，没有输出"
            
            finally:
                # 恢复标准输出
                sys.stdout = old_stdout
        
        except Exception as e:
            return f"代码执行错误: {str(e)}"
    
    async def _arun(self, code: str, timeout: int = 30) -> str:
        """异步执行代码"""
        return self._run(code, timeout)


class TextAnalyzerInput(BaseModel):
    """文本分析器输入模型"""
    text: str = Field(description="要分析的文本")
    operation: str = Field(description="操作类型: 'count' 统计字数, 'summary' 生成摘要, 'keywords' 提取关键词")


class TextAnalyzerTool(BaseTool):
    """文本分析器工具 - 分析文本内容"""
    
    name = "text_analyzer"
    description = "分析文本内容，包括字数统计、摘要生成、关键词提取等"
    args_schema: Type[BaseModel] = TextAnalyzerInput
    
    def _run(self, text: str, operation: str = "count") -> str:
        """
        执行文本分析
        
        Args:
            text: 要分析的文本
            operation: 操作类型
        
        Returns:
            str: 分析结果
        """
        try:
            if operation == "count":
                # 统计字数
                char_count = len(text)
                word_count = len(text.split())
                sentence_count = len(re.split(r'[.!?]+', text))
                
                return (
                    f"文本统计:\n"
                    f"字符数: {char_count}\n"
                    f"单词数: {word_count}\n"
                    f"句子数: {sentence_count}"
                )
            
            elif operation == "summary":
                # 生成简单摘要（取前200个字符）
                summary = text[:200] + "..." if len(text) > 200 else text
                return f"文本摘要:\n{summary}"
            
            elif operation == "keywords":
                # 简单的关键词提取（提取出现频率最高的词）
                words = re.findall(r'\b\w+\b', text.lower())
                word_freq = {}
                for word in words:
                    if len(word) > 3:  # 忽略短词
                        word_freq[word] = word_freq.get(word, 0) + 1
                
                # 获取前5个高频词
                top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:5]
                keywords = [word for word, freq in top_words]
                
                return f"关键词: {', '.join(keywords)}"
            
            else:
                return "不支持的操作类型"
        
        except Exception as e:
            return f"文本分析错误: {str(e)}"
    
    async def _arun(self, text: str, operation: str = "count") -> str:
        """异步执行文本分析"""
        return self._run(text, operation)


class WeatherInput(BaseModel):
    """天气查询输入模型"""
    city: str = Field(description="城市名称")


class WeatherTool(BaseTool):
    """天气查询工具 - 模拟天气查询"""
    
    name = "weather"
    description = "查询指定城市的天气信息"
    args_schema: Type[BaseModel] = WeatherInput
    
    def _run(self, city: str) -> str:
        """
        查询天气
        
        Args:
            city: 城市名称
        
        Returns:
            str: 天气信息
        """
        try:
            # 模拟天气数据
            # 在实际应用中，这里会调用真实的天气API
            weather_data = {
                'temperature': 25,
                'humidity': 60,
                'condition': '晴',
                'wind': '东风 3级',
                'aqi': 50
            }
            
            return (
                f"{city}天气信息:\n"
                f"温度: {weather_data['temperature']}°C\n"
                f"湿度: {weather_data['humidity']}%\n"
                f"天气: {weather_data['condition']}\n"
                f"风力: {weather_data['wind']}\n"
                f"空气质量指数: {weather_data['aqi']}"
            )
        
        except Exception as e:
            return f"天气查询错误: {str(e)}"
    
    async def _arun(self, city: str) -> str:
        """异步查询天气"""
        return self._run(city)


class UnitConverterInput(BaseModel):
    """单位转换输入模型"""
    value: float = Field(description="要转换的数值")
    from_unit: str = Field(description="原始单位")
    to_unit: str = Field(description="目标单位")
    conversion_type: str = Field(description="转换类型: 'length' 长度, 'weight' 重量, 'temperature' 温度")


class UnitConverterTool(BaseTool):
    """单位转换工具 - 进行单位转换"""
    
    name = "unit_converter"
    description = "进行单位转换，支持长度、重量、温度等"
    args_schema: Type[BaseModel] = UnitConverterInput
    
    def _run(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        conversion_type: str = "length"
    ) -> str:
        """
        执行单位转换
        
        Args:
            value: 数值
            from_unit: 原始单位
            to_unit: 目标单位
            conversion_type: 转换类型
        
        Returns:
            str: 转换结果
        """
        try:
            result = None
            
            if conversion_type == "length":
                # 长度转换（以米为基准）
                length_units = {
                    'm': 1,
                    'km': 1000,
                    'cm': 0.01,
                    'mm': 0.001,
                    'inch': 0.0254,
                    'foot': 0.3048,
                    'yard': 0.9144,
                    'mile': 1609.344
                }
                
                if from_unit in length_units and to_unit in length_units:
                    meters = value * length_units[from_unit]
                    result = meters / length_units[to_unit]
            
            elif conversion_type == "weight":
                # 重量转换（以千克为基准）
                weight_units = {
                    'kg': 1,
                    'g': 0.001,
                    'mg': 0.000001,
                    'lb': 0.453592,
                    'oz': 0.0283495
                }
                
                if from_unit in weight_units and to_unit in weight_units:
                    kg = value * weight_units[from_unit]
                    result = kg / weight_units[to_unit]
            
            elif conversion_type == "temperature":
                # 温度转换
                if from_unit == "c" and to_unit == "f":
                    result = value * 9/5 + 32
                elif from_unit == "f" and to_unit == "c":
                    result = (value - 32) * 5/9
                elif from_unit == "c" and to_unit == "k":
                    result = value + 273.15
                elif from_unit == "k" and to_unit == "c":
                    result = value - 273.15
                elif from_unit == to_unit:
                    result = value
            
            if result is not None:
                return f"{value} {from_unit} = {result:.2f} {to_unit}"
            else:
                return f"不支持的转换: {from_unit} 到 {to_unit}"
        
        except Exception as e:
            return f"单位转换错误: {str(e)}"
    
    async def _arun(
        self,
        value: float,
        from_unit: str,
        to_unit: str,
        conversion_type: str = "length"
    ) -> str:
        """异步执行单位转换"""
        return self._run(value, from_unit, to_unit, conversion_type)


def get_example_tools() -> list:
    """
    获取所有示例工具
    
    Returns:
        list: 工具实例列表
    """
    return [
        CalculatorTool(),
        SearchTool(),
        DateTimeTool(),
        CodeExecutorTool(),
        TextAnalyzerTool(),
        WeatherTool(),
        UnitConverterTool()
    ]
