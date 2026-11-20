from .base import *  # noqa: F401,F403

# Import dev settings by default; override with DJANGO_SETTINGS_MODULE env var
try:
    from .dev import *  # noqa: F401,F403
except ImportError:
    pass
