import json
import secrets
from datetime import datetime, timedelta
from typing import Tuple
from jose import JWTError, jwt
from app.core.current_user import CurrentUser


class TokenManager:
    """
    Token管理器
    
    负责JWT token的生成、验证和解析
    """
    def __init__(self, secret_key: str, algorithm: str = "HS256", expire_minutes: int = 120):
        """
        初始化Token管理器
        
        Args:
            secret_key: JWT签名密钥
            algorithm: 加密算法,默认HS256
            expire_minutes: 过期时间(分钟),默认120分钟
        """
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.expire_minutes = expire_minutes

    def generate_refresh_token(self) -> str:
        """
        生成刷新令牌
        
        Returns:
            32位URL安全的随机字符串
        """
        return secrets.token_urlsafe(32)

    def generate_token(self, user_claims: CurrentUser, refresh_token: str = None) -> Tuple[str, int]:
        """
        生成访问令牌
        
        Args:
            user_claims: 用户信息
            refresh_token: 刷新令牌(可选)
            
        Returns:
            JWT token和过期时间(分钟)
        """
        expire = datetime.utcnow() + timedelta(minutes=self.expire_minutes)
        to_encode = {
            "user_id": user_claims.user_id,
            "user_num": user_claims.user_num,
            "user_name": user_claims.user_name,
            "user_role": user_claims.user_role,
            "tenant_id": user_claims.tenant_id,
            "userrole_id": user_claims.userrole_id,
            "exp": int(expire.timestamp()),
            "iat": int(datetime.utcnow().timestamp())
        }
        if refresh_token:
            to_encode["refresh_token"] = refresh_token
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt, self.expire_minutes

    def get_current_user(self, token: str) -> CurrentUser:
        """
        从token中解析用户信息
        
        Args:
            token: JWT token
            
        Returns:
            用户信息,解析失败返回默认用户
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            user_id = payload.get("user_id")
            user_num = payload.get("user_num")
            user_name = payload.get("user_name")
            user_role = payload.get("user_role")
            tenant_id = payload.get("tenant_id")
            userrole_id = payload.get("userrole_id")
            
            if user_id is None:
                return CurrentUser()
            
            return CurrentUser(
                user_id=user_id,
                user_num=user_num,
                user_name=user_name,
                user_role=user_role,
                tenant_id=tenant_id,
                userrole_id=userrole_id
            )
        except JWTError:
            return CurrentUser()

    def decode_token(self, token: str) -> dict:
        """
        解码JWT token
        
        Args:
            token: JWT token字符串
            
        Returns:
            token payload字典，解码失败返回None
        """
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            return None

    def get_refresh_token_expire_minute(self) -> int:
        """
        获取刷新令牌过期时间
        
        Returns:
            过期时间(分钟)
        """
        return self.expire_minutes + 1
