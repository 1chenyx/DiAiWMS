from datetime import datetime
from sqlalchemy import BigInteger, Integer, String, DateTime, Boolean
from sqlalchemy.orm import mapped_column
from app.models import DeclBase


class WMSBaseModel(DeclBase):
    """
    WMS系统基础模型类
    
    所有数据库实体模型的基类,提供通用的字段定义和功能
    """
    __abstract__ = True

    id = mapped_column(Integer, primary_key=True, autoincrement=True, nullable=False, comment="主键ID")
