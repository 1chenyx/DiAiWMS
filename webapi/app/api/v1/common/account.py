from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.system.auth import (
    LoginInputViewModel, LoginOutputViewModel, RefreshTokenInputViewModel,
    EnterpriseRegisterInputViewModel, EnterpriseRegisterOutputViewModel
)
from app.services.system.account_service import AccountService
from app.core.token_manager import TokenManager
from app.core.database import get_master_db
from app.api.responses import success_response, error_response

_tag = "公共接口-账户认证"
router = APIRouter()


@router.post("/register")
async def register(
    register_input: EnterpriseRegisterInputViewModel,
    db: AsyncSession = Depends(get_master_db)
):
    """
    企业注册
    
    创建新企业租户和管理员账户
    
    Args:
        register_input: 企业注册信息
        db: 主库会话
        
    Returns:
        注册成功返回企业和管理员信息,失败返回错误信息
    """
    from app.initializer import g
    
    token_manager = TokenManager(
        secret_key=g.config.jwt_signing_key,
        expire_minutes=g.config.jwt_expire_minute
    )
    
    account_service = AccountService(db, token_manager)
    result, msg = await account_service.register_enterprise(register_input)
    
    if result:
        return success_response(result)
    else:
        return error_response(msg)


@router.post("/login")
async def login(
    login_input: LoginInputViewModel,
    db: AsyncSession = Depends(get_master_db)
):
    """
    用户登录
    
    Args:
        login_input: 登录信息(租户编号、用户名和密码)
        db: 主库会话
        
    Returns:
        登录成功返回token信息,失败返回错误信息
    """
    from app.initializer import g
    
    token_manager = TokenManager(
        secret_key=g.config.jwt_signing_key,
        expire_minutes=g.config.jwt_expire_minute
    )
    
    account_service = AccountService(db, token_manager)
    result = await account_service.login(login_input)
    
    if result:
        return success_response(result)
    else:
        return error_response("登录失败")


@router.post("/refresh-token")
async def refresh_token(
    refresh_input: RefreshTokenInputViewModel,
    db: AsyncSession = Depends(get_master_db)
):
    """
    刷新访问令牌
    
    Args:
        refresh_input: 刷新令牌信息(包含access_token和refresh_token)
        db: 主库会话
        
    Returns:
        刷新成功返回新的token信息,失败返回错误信息
    """
    from app.initializer import g
    
    token_manager = TokenManager(
        secret_key=g.config.jwt_signing_key,
        expire_minutes=g.config.jwt_expire_minute
    )
    
    account_service = AccountService(db, token_manager)
    result = await account_service.refresh_token(refresh_input.access_token, refresh_input.refresh_token)
    
    if result:
        return success_response(result)
    else:
        return error_response("刷新令牌失败")


@router.post("/hello-world")
async def hello_world():
    """
    测试接口
    
    Returns:
        返回Hello World
    """
    return success_response("Hello World")
