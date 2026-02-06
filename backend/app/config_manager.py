from typing import Dict, Any
import os
from .database import db

_cache: Dict[str, Any] = {}


def init_app_config(defaults: Dict[str, Any]):
    """Ensure `app_config` document exists and contains provided defaults.
    Stores the configuration in the `app_config` collection as a single document
    and updates the in-process environment so existing code using
    `os.getenv` continues to work.
    """
    client = db.get_client()
    db_name = os.getenv("MONGODB_DB") or "test"
    collection = client[db_name]["app_config"]

    # Find existing config document (singleton)
    config_doc = collection.find_one({})

    if not config_doc:
        config_doc = {"values": {}}

    values = config_doc.get("values", {})

    # Insert defaults only for missing keys
    updated = False
    for k, v in defaults.items():
        if k not in values or not values.get(k):
            values[k] = str(v)
            updated = True

    if updated or not config_doc.get("_id"):
        collection.replace_one({}, {"values": values}, upsert=True)

    # Cache and export to environment for compatibility
    _cache.clear()
    _cache.update(values)
    for k, v in values.items():
        if os.getenv(k) is None:
            os.environ[k] = str(v)


def get_config(key: str, default: Any = None) -> Any:
    """Get config value by key. Reads from cache or database if needed."""
    if key in _cache:
        return _cache[key]

    client = db.get_client()
    db_name = os.getenv("MONGODB_DB") or "test"
    collection = client[db_name]["app_config"]
    config_doc = collection.find_one({})
    if not config_doc:
        return default
    values = config_doc.get("values", {})
    _cache.update(values)
    return values.get(key, default)


def get_all_config() -> Dict[str, Any]:
    if _cache:
        return dict(_cache)
    client = db.get_client()
    db_name = os.getenv("MONGODB_DB") or "test"
    collection = client[db_name]["app_config"]
    config_doc = collection.find_one({})
    values = config_doc.get("values", {}) if config_doc else {}
    _cache.update(values)
    return dict(values)
