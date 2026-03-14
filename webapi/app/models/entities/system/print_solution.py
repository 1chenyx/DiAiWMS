from datetime import datetime
from sqlalchemy import Column, Integer, String, Numeric, BigInteger
from app.models.base import WMSBaseModel


class PrintSolution(WMSBaseModel):
    """
    打印方案实体类
    
    用于存储用户自定义的打印方案配置,包括报表尺寸、方向、配置JSON等
    """
    __tablename__ = "user_defined_print_solution"

    id = Column(Integer, primary_key=True, autoincrement=True, comment='主键ID')
    vue_path = Column(String(255), nullable=False, default='', comment='Vue路径')
    tab_page = Column(String(64), nullable=False, default='', comment='标签页')
    solution_name = Column(String(64), nullable=False, default='', comment='方案名称')
    config_json = Column(String(5000), nullable=True, comment='配置JSON')
    report_length = Column(Numeric(10, 2), nullable=False, default=0, comment='报表长度')
    report_width = Column(Numeric(10, 2), nullable=False, default=0, comment='报表宽度')
    report_direction = Column(String(16), nullable=False, default='', comment='报表方向')
    last_update_time = Column(BigInteger, nullable=False, default=lambda: int(datetime.now().timestamp()), comment='最后更新时间')
    tenant_id = Column(String(36), nullable=False, default='', comment='租户ID')
