from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import User, UserRole, Tenant
from app.schemas.system.auth import LoginInputViewModel, LoginOutputViewModel
from app.core.current_user import CurrentUser
from app.core.token_manager import TokenManager
from app.core.tenant_database import tenant_db_pool
from app.utils.md5_util import md5_encrypt_32
from app.api.dependencies import JWTUser


class AccountService:
    def __init__(self, db_session: AsyncSession, token_manager: TokenManager):
        self.db_session = db_session
        self.token_manager = token_manager

    async def login(self, login_input: LoginInputViewModel) -> Optional[LoginOutputViewModel]:
        md5_password = md5_encrypt_32(login_input.password)
        
        query = select(Tenant).where(
            Tenant.tenant_code == login_input.tenant_code,
            Tenant.is_valid == True
        )
        
        result = await self.db_session.execute(query)
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return None
        
        tenant_id = str(tenant.id)
        
        if not tenant_db_pool.tenant_exists(tenant_id):
            await tenant_db_pool.add_tenant_database(
                tenant_id=tenant_id,
                db_drivername=tenant.db_drivername,
                db_database=tenant.db_database,
                db_username=tenant.db_username,
                db_password=tenant.db_password,
                db_host=tenant.db_host,
                db_port=tenant.db_port,
                db_charset=tenant.db_charset,
                db_pool_size=tenant.db_pool_size,
                db_max_overflow=tenant.db_max_overflow,
                db_pool_recycle=tenant.db_pool_recycle,
                slave_host=tenant.slave_host,
                slave_port=tenant.slave_port,
            )
        
        tenant_db = await tenant_db_pool.get_tenant_session(tenant_id, use_slave=False)
        
        async with tenant_db:
            query = (
                select(User, UserRole)
                .join(UserRole, User.user_role == UserRole.role_name)
                .where(
                    UserRole.tenant_id == User.tenant_id,
                    User.tenant_id == tenant_id,
                    (User.user_name == login_input.user_name) | (User.user_num == login_input.user_name)
                )
            )
            
            result = await tenant_db.execute(query)
            rows = result.all()
            
            for user, user_role in rows:
                if user.auth_string == md5_password or user.auth_string == login_input.password:
                    current_user = CurrentUser(
                        user_id=user.id,
                        user_num=user.user_num,
                        user_name=user.user_name,
                        user_role=user.user_role,
                        tenant_id=tenant_id,
                        userrole_id=user_role.id
                    )
                    
                    refresh_token = self.token_manager.generate_refresh_token()
                    access_token, expire = self.token_manager.generate_token(current_user, refresh_token)
                    
                    await JWTUser.set_refresh_token(user.id, refresh_token)
                    
                    return LoginOutputViewModel(
                        user_num=user.user_num,
                        user_name=user.user_name,
                        user_id=user.id,
                        user_role=user.user_role,
                        userrole_id=user_role.id,
                        tenant_id=tenant_id,
                        expire=expire,
                        access_token=access_token,
                        refresh_token=refresh_token
                    )
        
        return None

    async def refresh_token(self, access_token: str, refresh_token: str) -> Optional[dict]:
        current_user = self.token_manager.get_current_user(access_token)
        if current_user.user_id == 1 and current_user.user_name == "admin":
            return None
        
        is_valid = await JWTUser.verify_refresh_token(current_user.user_id, refresh_token)
        if not is_valid:
            return None
        
        await JWTUser.remove_refresh_token(current_user.user_id)
        
        new_refresh_token = self.token_manager.generate_refresh_token()
        new_access_token, expire = self.token_manager.generate_token(current_user, new_refresh_token)
        
        await JWTUser.set_refresh_token(current_user.user_id, new_refresh_token)
        
        return {
            "access_token": new_access_token,
            "expire": expire,
            "refresh_token": new_refresh_token
        }
