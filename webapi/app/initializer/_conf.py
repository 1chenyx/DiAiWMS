import os
from pathlib import Path

from toollib.utils import ConfModel, FrozenVar

from app import APP_DIR

_CONFIG_DIR = APP_DIR.parent.joinpath("config")

dotenv_path = _CONFIG_DIR.joinpath(".env")
if os.environ.setdefault("app_env", "dev") == "prod":  # 生产环境不加载.env（请根据自身需求修改）
    dotenv_path = None
yaml_path = _CONFIG_DIR.joinpath(f"app_{os.environ.get('app_env', 'dev')}.yaml")


class Config(ConfModel):
    """配置"""
    app_dir: FrozenVar[Path] = APP_DIR
    # #
    app_env: str = "dev"
    yaml_path: Path = yaml_path
    api_keys: list = []
    jwt_key: str = ""
    # #
    app_title: str = "xApp"
    app_summary: str = "xxApp"
    app_description: str = "xxxApp"
    app_version: str = "1.0.0"
    app_debug: bool = True
    app_log_serialize: bool = False
    app_log_outdir: str = "./logs"
    app_disable_docs: bool = False
    app_allow_credentials: bool = True
    app_allow_origins: list = ["*"]
    app_allow_methods: list = ["*"]
    app_allow_headers: list = ["*"]
    # #
    db_drivername: str
    db_async_drivername: str
    db_database: str
    db_username: str = None
    db_password: str = None
    db_host: str = None
    db_port: int = None
    db_charset: str = None
    # 主从数据库配置
    db_slave_host: str = None
    db_slave_port: int = None
    # #
    jwt_audience: str = "ModernWMS"
    jwt_issuer: str = "ModernWMS"
    jwt_signing_key: str = "ModernWMS_SigningKey"
    jwt_expire_minute: int = 60
    # #
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: str = None


def init_config() -> Config:
    return Config(
        dotenv_path=dotenv_path,
        yaml_path=yaml_path,
    )
