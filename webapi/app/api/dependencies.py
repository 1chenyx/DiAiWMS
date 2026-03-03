from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, APIKeyHeader
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.sql.elements import quoted_name
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.api.exceptions import CustomException
from app.api.status import Status
from app.initializer import g
from app.utils.jwt_util import verify_jwt
from app.core.database import get_master_db, get_tenant_db
from app.core.current_user import CurrentUser
from app.utils.cache_manager import CacheManager


# -------------------- jwt --------------------

_REFRESH_TOKEN_COOKIE_NAME = "x_refresh_token"
_REFRESH_TOKEN_REDIS_PREFIX = "refresh_token"
_ACCESS_TOKEN_EXPIRE_MINUTES = 120
_REFRESH_TOKEN_EXPIRE_MINUTES = 121


class JWTUser(BaseModel):
    user_id: int = None
    user_num: str = None
    user_name: str = None
    user_role: str = None
    tenant_id: str = None
    userrole_id: int = None
    refresh_token: str = None
    exp: int = None
    iat: int = None

    @staticmethod
    def _get_refresh_token_key(user_id: int) -> str:
        return f"{_REFRESH_TOKEN_REDIS_PREFIX}_{user_id}"

    @staticmethod
    async def verify_refresh_token(user_id: int, token: str) -> bool:
        
        cache = CacheManager()
        redis_key = JWTUser._get_refresh_token_key(user_id)
        
        stored_token = cache.get(redis_key)
        
        result = stored_token == token
        return result

    @staticmethod
    async def set_refresh_token(user_id: int, token: str) -> bool:
        cache = CacheManager()
        redis_key = JWTUser._get_refresh_token_key(user_id)
        try:
            cache.set_absolute_expire(redis_key, token, _REFRESH_TOKEN_EXPIRE_MINUTES)
            return True
        except Exception as e:
            return False

    @staticmethod
    async def remove_refresh_token(user_id: int) -> bool:
        cache = CacheManager()
        redis_key = JWTUser._get_refresh_token_key(user_id)
        try:
            cache.remove(redis_key)
            return True
        except Exception as e:
            return False


class JWTAuthorizationCredentials(HTTPAuthorizationCredentials):
    jwt_user: JWTUser


async def verify_jwt_token(token: str, token_type: str) -> JWTUser:
    try:
        from app.utils.jwt_util import decode_jwt
        
        payload = decode_jwt(token=token)
        if payload is None:
            raise CustomException(status=Status.UNAUTHORIZED_ERROR)
        
        user_id = payload.get("user_id")
        if not user_id:
            raise CustomException(status=Status.UNAUTHORIZED_ERROR)
        
        if token_type == "access":
            refresh_token = payload.get("refresh_token")
            if not refresh_token:
                raise CustomException(status=Status.UNAUTHORIZED_ERROR)
            is_valid = await JWTUser.verify_refresh_token(user_id, refresh_token)
        else:
            is_valid = await JWTUser.verify_refresh_token(user_id, token)
        
        if not is_valid:
            raise CustomException(status=Status.UNAUTHORIZED_ERROR)
    except Exception as e:
        raise CustomException(status=Status.UNAUTHORIZED_ERROR, error=e)
    return JWTUser(**payload)


class JWTBearer(HTTPBearer):
    """从 Authorization header 获取 access_token"""

    async def __call__(self, request: Request) -> JWTAuthorizationCredentials | None:
        authorization = request.headers.get("Authorization")
        scheme, credentials = get_authorization_scheme_param(authorization)
        if not (authorization and scheme and credentials):
            return None
        if scheme.lower() != "bearer":
            return None
        try:
            jwt_user = await verify_jwt_token(credentials, token_type="access")
            return JWTAuthorizationCredentials(scheme=scheme, credentials=credentials, jwt_user=jwt_user)
        except Exception:
            return None


class JWTCookie:
    """从 Cookie 获取 refresh_token"""

    def __init__(self, cookie_name: str = _REFRESH_TOKEN_COOKIE_NAME, auto_error: bool = True):
        self.cookie_name = cookie_name
        self.auto_error = auto_error

    async def __call__(self, request: Request) -> JWTUser | None:
        token = request.cookies.get(self.cookie_name)
        if not token:
            return None
        try:
            return await verify_jwt_token(token, token_type="refresh")
        except Exception:
            return None


async def get_current_user(
    credentials: JWTAuthorizationCredentials | None = Depends(JWTBearer(auto_error=False))
) -> CurrentUser:
    """获取当前用户，用于认证 access token（从 Authorization header）"""
    if not credentials or not credentials.jwt_user or not credentials.jwt_user.user_id:
        return CurrentUser()
    jwt_user = credentials.jwt_user
    return CurrentUser(
        user_id=jwt_user.user_id,
        user_num=jwt_user.user_num,
        user_name=jwt_user.user_name,
        user_role=jwt_user.user_role,
        tenant_id=jwt_user.tenant_id,
        userrole_id=jwt_user.userrole_id,
        is_authenticated=True
    )


async def get_current_user_from_refresh_token(
    jwt_user: JWTUser | None = Depends(JWTCookie(auto_error=False))
) -> JWTUser:
    """获取当前用户，用于认证 refresh token（从 Cookie）"""
    if not jwt_user or not jwt_user.user_id:
        return CurrentUser()
    return CurrentUser(
        user_id=jwt_user.user_id,
        user_num=jwt_user.user_num,
        user_name=jwt_user.user_name,
        user_role=jwt_user.user_role,
        tenant_id=jwt_user.tenant_id,
        userrole_id=jwt_user.userrole_id,
        is_authenticated=True
    )


# -------------------- api key --------------------

_API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)


async def get_current_api_key(
    api_key: str | None = Security(_API_KEY_HEADER)
) -> str:
    """获取当前 api key, 用于认证 api key"""
    if not api_key:
        raise CustomException(status=Status.UNAUTHORIZED_ERROR, error="API key is missing or empty")
    if api_key not in g.config.api_keys:
        raise CustomException(status=Status.UNAUTHORIZED_ERROR, error="Invalid API key")
    return api_key


# -------------------- tenant database --------------------

async def get_db_by_tenant(
    current_user: CurrentUser = Depends(get_current_user)
) -> AsyncSession:
    """
    根据当前用户的租户ID获取对应的数据库会话(写操作使用主库)
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        租户数据库异步会话对象
    """
    if not current_user.tenant_id or not current_user.is_authenticated:
        for session in get_master_db():
            yield session
            return
    async for session in get_tenant_db(current_user.tenant_id, use_slave=False):
        yield session


async def get_db_by_tenant_read(
    current_user: CurrentUser = Depends(get_current_user)
) -> AsyncSession:
    """
    根据当前用户的租户ID获取对应的数据库会话(读操作使用从库)
    
    Args:
        current_user: 当前登录用户
        
    Returns:
        租户数据库异步会话对象
    """
    if not current_user.tenant_id or not current_user.is_authenticated:
        for session in get_master_db():
            yield session
            return
    async for session in get_tenant_db(current_user.tenant_id, use_slave=True):
        yield session


async def get_master_db_session() -> AsyncSession:
    """
    获取主库会话(用于租户管理模块)
    
    Returns:
        主库异步会话对象
    """
    return get_master_db()
