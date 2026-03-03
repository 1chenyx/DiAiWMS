from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.token_manager import TokenManager
from app.core.current_user import CurrentUser
from app.initializer import g


security = HTTPBearer()


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> CurrentUser:
    """
    获取当前登录用户
    
    Args:
        credentials: HTTP授权凭证
        
    Returns:
        当前用户信息
        
    Raises:
        HTTPException: 当认证失败时抛出401错误
    """
    try:
        token_manager = TokenManager(
            secret_key=g.config.jwt_signing_key,
            expire_minutes=g.config.jwt_expire_minute
        )
        payload = token_manager.decode_token(credentials.credentials)
        
        if not payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
            )
        
        return CurrentUser(
            user_id=payload.get("user_id", 1),
            user_num=payload.get("user_num", "admin"),
            user_name=payload.get("user_name", "admin"),
            user_role=payload.get("user_role", "admin"),
            tenant_id=payload.get("tenant_id", 1),
            userrole_id=payload.get("userrole_id", 1),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
