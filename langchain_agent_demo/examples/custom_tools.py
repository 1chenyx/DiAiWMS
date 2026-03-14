"""
LangChain Agent Demo - 示例工具（用于自动发现）
这些工具演示了如何使用工具元数据装饰器
"""
from langchain.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import random
import string
from tools.manager import tool_metadata


class PasswordGeneratorInput(BaseModel):
    """密码生成器输入模型"""
    length: int = Field(default=12, description="密码长度", ge=4, le=50)
    include_uppercase: bool = Field(default=True, description="包含大写字母")
    include_lowercase: bool = Field(default=True, description="包含小写字母")
    include_numbers: bool = Field(default=True, description="包含数字")
    include_symbols: bool = Field(default=False, description="包含特殊字符")


@tool_metadata(
    name="password_generator",
    description="生成安全的随机密码",
    version="1.0.0",
    author="LangChain Agent Demo",
    category="security",
    enabled=True,
    tags=["security", "random", "password"]
)
class PasswordGeneratorTool(BaseTool):
    """密码生成器工具 - 生成安全的随机密码"""
    
    name = "password_generator"
    description = "生成安全的随机密码，支持自定义长度和字符类型"
    args_schema: Type[BaseModel] = PasswordGeneratorInput
    
    def _run(
        self,
        length: int = 12,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_numbers: bool = True,
        include_symbols: bool = False
    ) -> str:
        """
        生成密码
        
        Args:
            length: 密码长度
            include_uppercase: 包含大写字母
            include_lowercase: 包含小写字母
            include_numbers: 包含数字
            include_symbols: 包含特殊字符
        
        Returns:
            str: 生成的密码
        """
        try:
            characters = ""
            
            if include_uppercase:
                characters += string.ascii_uppercase
            if include_lowercase:
                characters += string.ascii_lowercase
            if include_numbers:
                characters += string.digits
            if include_symbols:
                characters += string.punctuation
            
            if not characters:
                characters = string.ascii_letters + string.digits
            
            password = ''.join(random.choice(characters) for _ in range(length))
            
            return f"生成的密码: {password}"
        
        except Exception as e:
            return f"密码生成错误: {str(e)}"
    
    async def _arun(
        self,
        length: int = 12,
        include_uppercase: bool = True,
        include_lowercase: bool = True,
        include_numbers: bool = True,
        include_symbols: bool = False
    ) -> str:
        """异步生成密码"""
        return self._run(length, include_uppercase, include_lowercase, include_numbers, include_symbols)


class ColorConverterInput(BaseModel):
    """颜色转换器输入模型"""
    color: str = Field(description="颜色值，支持HEX、RGB、HSL等格式")
    from_format: str = Field(default="hex", description="输入格式: hex, rgb, hsl")
    to_format: str = Field(default="rgb", description="输出格式: hex, rgb, hsl")


@tool_metadata(
    name="color_converter",
    description="颜色格式转换工具",
    version="1.0.0",
    author="LangChain Agent Demo",
    category="utility",
    enabled=True,
    tags=["color", "converter", "utility"]
)
class ColorConverterTool(BaseTool):
    """颜色转换器工具 - 在不同颜色格式之间转换"""
    
    name = "color_converter"
    description = "在HEX、RGB、HSL等颜色格式之间进行转换"
    args_schema: Type[BaseModel] = ColorConverterInput
    
    def _run(self, color: str, from_format: str = "hex", to_format: str = "rgb") -> str:
        """
        转换颜色格式
        
        Args:
            color: 颜色值
            from_format: 输入格式
            to_format: 输出格式
        
        Returns:
            str: 转换后的颜色值
        """
        try:
            # 简化的颜色转换实现
            # 实际应用中需要更完整的颜色转换逻辑
            
            if from_format == "hex" and to_format == "rgb":
                # HEX转RGB
                hex_color = color.lstrip('#')
                rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
                return f"RGB({rgb[0]}, {rgb[1]}, {rgb[2]})"
            
            elif from_format == "rgb" and to_format == "hex":
                # RGB转HEX
                rgb_values = [int(x.strip()) for x in color.replace('rgb', '').replace('(', '').replace(')', '').split(',')]
                hex_color = '#{:02x}{:02x}{:02x}'.format(*rgb_values)
                return hex_color.upper()
            
            else:
                return f"暂不支持从 {from_format} 到 {to_format} 的转换"
        
        except Exception as e:
            return f"颜色转换错误: {str(e)}"
    
    async def _arun(self, color: str, from_format: str = "hex", to_format: str = "rgb") -> str:
        """异步转换颜色"""
        return self._run(color, from_format, to_format)


class QrCodeGeneratorInput(BaseModel):
    """二维码生成器输入模型"""
    text: str = Field(description="要编码的文本内容")
    size: int = Field(default=200, description="二维码尺寸（像素）", ge=50, le=1000)


@tool_metadata(
    name="qr_code_generator",
    description="生成二维码图片",
    version="1.0.0",
    author="LangChain Agent Demo",
    category="utility",
    enabled=True,
    tags=["qr", "code", "generator", "image"]
)
class QrCodeGeneratorTool(BaseTool):
    """二维码生成器工具 - 生成二维码图片"""
    
    name = "qr_code_generator"
    description = "生成二维码图片，支持自定义内容和尺寸"
    args_schema: Type[BaseModel] = QrCodeGeneratorInput
    
    def _run(self, text: str, size: int = 200) -> str:
        """
        生成二维码
        
        Args:
            text: 要编码的文本
            size: 二维码尺寸
        
        Returns:
            str: 生成结果
        """
        try:
            # 检查是否有qrcode库
            try:
                import qrcode
            except ImportError:
                return "需要安装qrcode库: pip install qrcode[pil]"
            
            # 生成二维码
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(text)
            qr.make(fit=True)
            
            # 创建图片
            img = qr.make_image(fill_color="black", back_color="white")
            
            # 调整大小
            img = img.resize((size, size))
            
            # 保存图片
            filename = f"qrcode_{hash(text)}.png"
            img.save(filename)
            
            return f"二维码已生成并保存为: {filename}"
        
        except Exception as e:
            return f"二维码生成错误: {str(e)}"
    
    async def _arun(self, text: str, size: int = 200) -> str:
        """异步生成二维码"""
        return self._run(text, size)


class JsonFormatterInput(BaseModel):
    """JSON格式化器输入模型"""
    json_string: str = Field(description="要格式化的JSON字符串")
    indent: int = Field(default=2, description="缩进空格数", ge=0, le=8)


@tool_metadata(
    name="json_formatter",
    description="格式化和验证JSON字符串",
    version="1.0.0",
    author="LangChain Agent Demo",
    category="utility",
    enabled=True,
    tags=["json", "formatter", "validation"]
)
class JsonFormatterTool(BaseTool):
    """JSON格式化器工具 - 格式化和验证JSON字符串"""
    
    name = "json_formatter"
    description = "格式化和验证JSON字符串，使其更易读"
    args_schema: Type[BaseModel] = JsonFormatterInput
    
    def _run(self, json_string: str, indent: int = 2) -> str:
        """
        格式化JSON
        
        Args:
            json_string: JSON字符串
            indent: 缩进空格数
        
        Returns:
            str: 格式化后的JSON
        """
        try:
            import json
            
            # 解析JSON
            data = json.loads(json_string)
            
            # 格式化
            formatted_json = json.dumps(data, indent=indent, ensure_ascii=False)
            
            return f"格式化后的JSON:\n{formatted_json}"
        
        except json.JSONDecodeError as e:
            return f"JSON解析错误: {str(e)}"
        except Exception as e:
            return f"JSON格式化错误: {str(e)}"
    
    async def _arun(self, json_string: str, indent: int = 2) -> str:
        """异步格式化JSON"""
        return self._run(json_string, indent)


class UrlEncoderInput(BaseModel):
    """URL编码器输入模型"""
    text: str = Field(description="要编码或解码的文本")
    operation: str = Field(default="encode", description="操作类型: encode, decode")


@tool_metadata(
    name="url_encoder",
    description="URL编码和解码工具",
    version="1.0.0",
    author="LangChain Agent Demo",
    category="utility",
    enabled=True,
    tags=["url", "encode", "decode", "utility"]
)
class UrlEncoderTool(BaseTool):
    """URL编码器工具 - 进行URL编码和解码"""
    
    name = "url_encoder"
    description = "对URL进行编码或解码操作"
    args_schema: Type[BaseModel] = UrlEncoderInput
    
    def _run(self, text: str, operation: str = "encode") -> str:
        """
        URL编码或解码
        
        Args:
            text: 文本
            operation: 操作类型
        
        Returns:
            str: 编码或解码后的结果
        """
        try:
            from urllib.parse import quote, unquote
            
            if operation == "encode":
                result = quote(text)
                return f"URL编码结果: {result}"
            elif operation == "decode":
                result = unquote(text)
                return f"URL解码结果: {result}"
            else:
                return "不支持的操作类型，请使用 'encode' 或 'decode'"
        
        except Exception as e:
            return f"URL编码/解码错误: {str(e)}"
    
    async def _arun(self, text: str, operation: str = "encode") -> str:
        """异步URL编码/解码"""
        return self._run(text, operation)
