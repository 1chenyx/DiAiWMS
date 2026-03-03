import json
from typing import Mapping, Any

from fastapi.encoders import jsonable_encoder
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse, StreamingResponse, ContentStream
from toollib.utils import map_jsontype

from app.api.status import Status
from app.initializer.context import request_id_var

_EXPOSE_ERROR = True


class Responses:
    """
    响应工具类
    
    提供统一的响应格式和响应方法
    """

    @staticmethod
    def success(
        data: dict | list | str | None = None,
        msg: str = None,
        code: int = None,
        status: Status = Status.SUCCESS,
        is_encode_data: bool = False,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> JSONResponse:
        """
        成功响应
        
        Args:
            data: 响应数据
            msg: 响应消息
            code: 响应码
            status: 状态对象
            is_encode_data: 是否编码数据
            status_code: HTTP状态码
            headers: 响应头
            media_type: 媒体类型
            background: 后台任务
            
        Returns:
            JSON响应对象
        """
        content = {
            "isSuccess": True,
            "msg": msg or status.msg,
            "code": code or status.code,
            "data": Responses.encode_data(data) if is_encode_data else data,
        }
        return JSONResponse(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    @staticmethod
    def failure(
        msg: str = None,
        code: int = None,
        error: str | Exception | None = None,
        data: dict | list | str | None = None,
        status: Status = Status.FAILURE,
        is_encode_data: bool = False,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> JSONResponse:
        """
        失败响应
        
        Args:
            msg: 响应消息
            code: 响应码
            error: 错误信息
            data: 响应数据
            status: 状态对象
            is_encode_data: 是否编码数据
            status_code: HTTP状态码
            headers: 响应头
            media_type: 媒体类型
            background: 后台任务
            
        Returns:
            JSON响应对象
        """
        content = {
            "isSuccess": False,
            "msg": msg or status.msg,
            "code": code or status.code,
            "data": Responses.encode_data(data) if is_encode_data else data,
        }
        if _EXPOSE_ERROR:
            content["error"] = str(error) if error else None
        return JSONResponse(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    @staticmethod
    def encode_data(data: Any) -> Any:
        """
        编码数据为JSON可序列化格式
        
        Args:
            data: 待编码的数据
            
        Returns:
            编码后的数据
        """
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        if isinstance(data, (dict, list)):
            try:
                json.dumps(data)
                return data
            except (TypeError, OverflowError):
                pass
        return jsonable_encoder(data)

    @staticmethod
    def stream(
        content: ContentStream,
        status_code: int = 200,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> StreamingResponse:
        """
        流式响应
        
        Args:
            content: 流内容
            status_code: HTTP状态码
            headers: 响应头
            media_type: 媒体类型
            background: 后台任务
            
        Returns:
            流式响应对象
        """
        return StreamingResponse(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )


def response_docs(
    data: dict = None,  # data文档（key=字段名，value=字段类型或示例）
    docs_extra: dict = None,
):
    """
    响应文档生成器
    
    Args:
        data: 数据文档
        docs_extra: 额外文档
        
    Returns:
        响应文档字典
    """

    def _format_value(value):
        if isinstance(value, str):
            _value = value.split("|")
            if len(_value) > 1:
                return " | ".join([map_jsontype(_v.strip(), is_keep_integer=True) for _v in _value])
            return map_jsontype(value, is_keep_integer=True)
        elif isinstance(value, dict):
            return {k: _format_value(v) for k, v in value.items()}
        elif isinstance(value, (list, tuple)):
            return [_format_value(item) for item in value]
        else:
            return str(value)

    format_data = _format_value(data) if data else "object | array | ..."

    docs = {
        200: {
            "description": "操作成功【code为0 & http状态码200】",
            "content": {
                "application/json": {
                    "example": {
                        "isSuccess": True,
                        "msg": "string",
                        "code": "integer",
                        "data": format_data,
                    }
                }
            }
        },
        422: {
            "description": "操作失败【code非0 & http状态码200】",
            "content": {
                "application/json": {
                    "example": {
                        "isSuccess": False,
                        "msg": "string",
                        "code": "integer",
                        "error": "string",
                        "data": "object | array | ...",
                    }
                }
            }
        },
    }
    if docs_extra:
        docs.update(docs_extra)
    return docs


def success_response(data: dict | list | str | None = None, msg: str = None, code: int = None):
    """
    成功响应快捷方法
    
    Args:
        data: 响应数据
        msg: 响应消息
        code: 响应码
        
    Returns:
        JSON响应对象
    """
    from pydantic import BaseModel
    
    def serialize_data(item):
        if item is None:
            return None
        if isinstance(item, BaseModel):
            return item.model_dump()
        if isinstance(item, list):
            return [serialize_data(i) for i in item]
        if isinstance(item, dict):
            return {k: serialize_data(v) for k, v in item.items()}
        return item
    
    serialized_data = serialize_data(data)
    return Responses.success(data=serialized_data, msg=msg, code=code)


def error_response(msg: str = None, code: int = None, error: str | Exception | None = None):
    """
    错误响应快捷方法
    
    Args:
        msg: 响应消息
        code: 响应码
        error: 错误信息
        
    Returns:
        JSON响应对象
    """
    return Responses.failure(msg=msg, code=code, error=error)
