from datetime import datetime, timedelta
from typing import Any, Optional

class InMemoryCache:
    def __init__(self):
        self._store = {}

    def set(self, key: str, value: Any, ttl: int = 3600):
        expire = datetime.utcnow() + timedelta(seconds=ttl)
        self._store[key] = (value, expire)

    def get(self, key: str) -> Optional[Any]:
        if key in self._store:
            value, expire = self._store[key]
            if datetime.utcnow() < expire:
                return value
            del self._store[key]
        return None

cache = InMemoryCache()