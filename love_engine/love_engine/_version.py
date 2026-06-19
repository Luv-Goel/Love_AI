import importlib_metadata

try:
    version = importlib_metadata.version("love_engine")
except Exception:
    version = "unknown"
