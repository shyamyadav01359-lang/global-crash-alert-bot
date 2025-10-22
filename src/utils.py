import os

def env(name, default=None, cast=str):
    val = os.getenv(name, default)
    if val is None:
        return None
    try:
        return cast(val)
    except Exception:
        return val
