from datetime import datetime
from sqlalchemy import String, Boolean, BigInteger
from sqlalchemy.orm import mapped_column
from app.models.base import WMSBaseModel
from app.utils.convert_util import min_date


class User(WMSBaseModel):
    """
    用户实体类
    
    用于存储系统用户的基本信息,包括用户编号、用户名、联系方式、角色、权限等
    """
    __tablename__ = "user"

    user_num = mapped_column(String(50), nullable=False, default="", comment="用户编号")
    user_name = mapped_column(String(100), nullable=False, default="", comment="用户名")
    contact_tel = mapped_column(String(20), nullable=False, default="", comment="联系电话")
    user_role = mapped_column(String(50), nullable=False, default="", comment="用户角色")
    sex = mapped_column(String(10), nullable=False, default="", comment="性别")
    is_valid = mapped_column(Boolean, nullable=False, default=False, comment="是否有效")
    auth_string = mapped_column(String(255), nullable=False, default="", comment="密码")
    email = mapped_column(String(100), nullable=False, default="", comment="邮箱")
    creator = mapped_column(String(50), nullable=False, default="", comment="创建人")
    create_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="创建时间")
    last_update_time = mapped_column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment="最后更新时间")
    tenant_id = mapped_column(String(36), nullable=False, default="", comment="租户ID")
