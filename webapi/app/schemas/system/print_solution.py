from pydantic import BaseModel, Field


class PrintSolutionCreate(BaseModel):
    vue_path: str = Field(..., max_length=255, description='Vue路径')
    tab_page: str = Field(..., max_length=64, description='标签页')
    solution_name: str = Field(..., max_length=64, description='方案名称')
    config_json: str = Field(None, max_length=5000, description='配置JSON')
    report_length: float = Field(0, description='报表长度')
    report_width: float = Field(0, description='报表宽度')
    report_direction: str = Field('', max_length=16, description='报表方向')


class PrintSolutionUpdate(BaseModel):
    id: int
    vue_path: str = Field(..., max_length=255, description='Vue路径')
    tab_page: str = Field(..., max_length=64, description='标签页')
    solution_name: str = Field(..., max_length=64, description='方案名称')
    config_json: str = Field(None, max_length=5000, description='配置JSON')
    report_length: float = Field(0, description='报表长度')
    report_width: float = Field(0, description='报表宽度')
    report_direction: str = Field('', max_length=16, description='报表方向')


class PrintSolutionViewModel(BaseModel):
    id: int
    vue_path: str
    tab_page: str
    solution_name: str
    config_json: str
    report_length: float
    report_width: float
    report_direction: str
    last_update_time: int
    tenant_id: str

    class Config:
        from_attributes = True
