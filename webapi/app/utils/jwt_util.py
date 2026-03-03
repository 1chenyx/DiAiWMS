"""
JWT工具模块

提供JWT token的生成、验证和解析功能
"""
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.initializer import g


def verify_jwt(
    token: str,
    jwt_key: Optional[str] = None,
    token_type: str = "access"
) -> Optional[Dict[str, Any]]:
    """
    验证JWT token
    
    Args:
        token: JWT token字符串
        jwt_key: JWT签名密钥,如果为None则使用配置中的密钥
        token_type: token类型(access或refresh)
        
    Returns:
        解析后的payload,验证失败返回None
    """
    try:
        secret_key = jwt_key or g.config.jwt_signing_key
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"],
            options={"verify_exp": True}
        )
        return payload
    except JWTError:
        return None


def generate_jwt(
    payload: Dict[str, Any],
    secret_key: Optional[str] = None,
    expire_minutes: int = 60
) -> str:
    """
    生成JWT token
    
    Args:
        payload: 要编码的数据
        secret_key: JWT签名密钥,如果为None则使用配置中的密钥
        expire_minutes: 过期时间(分钟)
        
    Returns:
        JWT token字符串
    """
    secret_key = secret_key or g.config.jwt_signing_key
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    payload["exp"] = expire
    payload["iat"] = datetime.utcnow()
    
    encoded_jwt = jwt.encode(payload, secret_key, algorithm="HS256")
    return encoded_jwt


def decode_jwt(
    token: str,
    jwt_key: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    """
    解码JWT token(不验证过期时间)
    
    Args:
        token: JWT token字符串
        jwt_key: JWT签名密钥,如果为None则使用配置中的密钥
        
    Returns:
        解析后的payload,解码失败返回None
    """
    try:
        secret_key = jwt_key or g.config.jwt_signing_key
        payload = jwt.decode(
            token,
            secret_key,
            algorithms=["HS256"],
            options={"verify_exp": False}
        )
        return payload
    except JWTError:
        return None
