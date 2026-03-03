import json
import redis
from typing import Optional, Any
from datetime import timedelta
import logging
from app.initializer._conf import Config

logger = logging.getLogger(__name__)


class CacheManager:
    _instance = None
    _redis_client = None
    _config = None
    _memory_cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CacheManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if self._redis_client is None:
            try:
                if self._config is None:
                    from app.initializer._conf import Config, _CONFIG_DIR, yaml_path
                    self._config = Config(
                        dotenv_path=_CONFIG_DIR.joinpath(".env"),
                        yaml_path=yaml_path,
                    )
                
                if self._config is None:
                    raise Exception("Config is not initialized")
                
                self._redis_client = redis.Redis(
                    host=self._config.redis_host,
                    port=self._config.redis_port,
                    db=self._config.redis_db,
                    password=self._config.redis_password,
                    decode_responses=True,
                    socket_connect_timeout=5
                )
                
                # 测试连接
                self._redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}, using in-memory cache")
                self._redis_client = None

    def get(self, key: str) -> Optional[Any]:
        if not key or not key.strip():
            raise ValueError("Key cannot be empty")
        
        if self._redis_client:
            try:
                value = self._redis_client.get(key)
                if value:
                    try:
                        return json.loads(value)
                    except json.JSONDecodeError:
                        return value
            except Exception as e:
                logger.error(f"Redis get error: {e}")
        else:
            return self._memory_cache.get(key)

        return None

    def set_not_expire(self, key: str, value: Any):
        if not key or not key.strip():
            raise ValueError("Key cannot be empty")

        if self._redis_client:
            try:
                self._redis_client.set(key, json.dumps(value, ensure_ascii=False))
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        else:
            self._memory_cache[key] = value

    def set_sliding_expire(self, key: str, value: Any, expire_minutes: int):
        if not key or not key.strip():
            raise ValueError("Key cannot be empty")

        if self._redis_client:
            try:
                expire_seconds = int(timedelta(minutes=expire_minutes).total_seconds())
                self._redis_client.setex(
                    key,
                    expire_seconds,
                    json.dumps(value, ensure_ascii=False)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        else:
            self._memory_cache[key] = value

    def set_absolute_expire(self, key: str, value: Any, expire_minutes: int):
        if not key or not key.strip():
            raise ValueError("Key cannot be empty")

        if self._redis_client:
            try:
                expire_seconds = int(timedelta(minutes=expire_minutes).total_seconds())
                if isinstance(value, str):
                    serialized_value = value
                else:
                    serialized_value = json.dumps(value, ensure_ascii=False)
                
                self._redis_client.setex(key, expire_seconds, serialized_value)
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        else:
            self._memory_cache[key] = value

    def set_sliding_and_absolute_expire(
        self,
        key: str,
        value: Any,
        sliding_minutes: int,
        absolute_minutes: int
    ):
        if not key or not key.strip():
            raise ValueError("Key cannot be empty")

        if self._redis_client:
            try:
                self._redis_client.setex(
                    key,
                    timedelta(minutes=absolute_minutes),
                    json.dumps(value, ensure_ascii=False)
                )
            except Exception as e:
                logger.error(f"Redis set error: {e}")
        else:
            self._memory_cache[key] = value

    def remove(self, key: str):
        if not key or not key.strip():
            raise ValueError("Key cannot be empty")

        if self._redis_client:
            try:
                self._redis_client.delete(key)
            except Exception as e:
                logger.error(f"Redis delete error: {e}")
        else:
            self._memory_cache.pop(key, None)

    def is_token_exist(self, user_id: int, token_type: str, expire_minutes: int) -> bool:
        key = f"ModernWMS_{token_type}_{user_id}"
        value = self.get(key)
        if value:
            self.set_sliding_expire(key, value, expire_minutes)
            return True
        return False

    async def token_set(self, user_id: int, token_type: str, token: str, expire_minutes: int) -> bool:
        key = f"ModernWMS_{token_type}_{user_id}"
        try:
            self.set_absolute_expire(key, token, expire_minutes)
            return True
        except Exception as e:
            logger.error(f"Token set error: {e}")
            return False

    def dispose(self):
        if self._redis_client:
            try:
                self._redis_client.close()
            except Exception as e:
                logger.error(f"Redis close error: {e}")
