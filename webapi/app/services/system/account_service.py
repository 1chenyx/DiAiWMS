from typing import Optional, Tuple
from datetime import datetime
import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.entities import User, UserRole, Tenant
from app.schemas.system.auth import (
    LoginInputViewModel, LoginOutputViewModel,
    EnterpriseRegisterInputViewModel, EnterpriseRegisterOutputViewModel
)
from app.core.current_user import CurrentUser
from app.core.token_manager import TokenManager
from app.core.tenant_database import tenant_db_pool
from app.utils.md5_util import md5_encrypt_32
from app.api.dependencies import JWTUser


class AccountService:
    def __init__(self, db_session: AsyncSession, token_manager: TokenManager):
        self.db_session = db_session
        self.token_manager = token_manager

    async def register_enterprise(
        self,
        register_input: EnterpriseRegisterInputViewModel
    ) -> Tuple[Optional[EnterpriseRegisterOutputViewModel], str]:
        """
        企业注册
        
        创建新租户和管理员账户
        
        Args:
            register_input: 企业注册输入数据
            
        Returns:
            (注册结果, 错误信息)
        """
        existing_tenant = await self.db_session.execute(
            select(Tenant).where(Tenant.tenant_code == register_input.tenant_code)
        )
        if existing_tenant.scalar_one_or_none():
            return None, "企业编码已存在，请更换"
        
        tenant_id = str(uuid.uuid4())
        current_time = int(datetime.now().timestamp())
        
        from app.initializer import g
        default_db_config = {
            'db_drivername': g.config.db_drivername,
            'db_database': g.config.db_database,
            'db_username': g.config.db_username,
            'db_password': g.config.db_password,
            'db_host': g.config.db_host,
            'db_port': g.config.db_port,
            'db_charset': g.config.db_charset,
            'db_pool_size': 10,
            'db_max_overflow': 5,
            'db_pool_recycle': 3600,
        }
        
        new_tenant = Tenant(
            id=tenant_id,
            tenant_name=register_input.tenant_name,
            tenant_code=register_input.tenant_code,
            contact_person=register_input.contact_person,
            contact_phone=register_input.contact_phone,
            contact_email=register_input.contact_email,
            address=register_input.address or "",
            description=register_input.description or "",
            db_drivername=default_db_config['db_drivername'],
            db_database=default_db_config['db_database'],
            db_username=default_db_config['db_username'],
            db_password=default_db_config['db_password'],
            db_host=default_db_config['db_host'],
            db_port=default_db_config['db_port'],
            db_charset=default_db_config['db_charset'],
            db_pool_size=default_db_config['db_pool_size'],
            db_max_overflow=default_db_config['db_max_overflow'],
            db_pool_recycle=default_db_config['db_pool_recycle'],
            is_valid=True,
            creator=register_input.admin_user_name,
            create_time=current_time,
            last_update_time=current_time
        )
        
        self.db_session.add(new_tenant)
        await self.db_session.commit()
        
        try:
            await tenant_db_pool.add_tenant_database(
                tenant_id=tenant_id,
                **default_db_config
            )
        except Exception as e:
            await self._rollback_tenant(tenant_id)
            return None, f"创建租户数据库连接失败: {str(e)}"
        
        tenant_db = await tenant_db_pool.get_tenant_session(tenant_id, use_slave=False)
        
        try:
            admin_role = UserRole(
                role_name='admin',
                is_valid=True,
                tenant_id=tenant_id,
                create_time=current_time,
                last_update_time=current_time
            )
            tenant_db.add(admin_role)
            await tenant_db.flush()
            
            md5_password = md5_encrypt_32(register_input.admin_password)
            admin_user = User(
                user_num='admin',
                user_name=register_input.admin_user_name,
                user_role='admin',
                auth_string=md5_password,
                contact_tel=register_input.admin_contact_tel or "",
                email=register_input.admin_email or register_input.contact_email,
                is_valid=True,
                tenant_id=tenant_id,
                creator=register_input.admin_user_name,
                create_time=current_time,
                last_update_time=current_time
            )
            tenant_db.add(admin_user)
            await tenant_db.commit()
            await tenant_db.refresh(admin_user)
            
            return EnterpriseRegisterOutputViewModel(
                tenant_id=tenant_id,
                tenant_name=register_input.tenant_name,
                tenant_code=register_input.tenant_code,
                user_id=admin_user.id,
                user_name=admin_user.user_name
            ), "注册成功"
            
        except Exception as e:
            await tenant_db.rollback()
            await self._rollback_tenant(tenant_id)
            return None, f"创建管理员账户失败: {str(e)}"
        finally:
            await tenant_db.close()
    
    async def _rollback_tenant(self, tenant_id: str):
        """
        回滚租户创建
        
        删除已创建的租户记录和连接池
        
        Args:
            tenant_id: 租户ID
        """
        try:
            await tenant_db_pool.remove_tenant_database(tenant_id)
        except Exception:
            pass
        
        try:
            await self.db_session.execute(
                Tenant.__table__.delete().where(Tenant.id == tenant_id)
            )
            await self.db_session.commit()
        except Exception:
            await self.db_session.rollback()

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
