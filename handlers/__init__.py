# handlers/__init__.py
from .schedule_handlers import router as schedule_router
from .settings_handlers import router as settings_router

__all__ = ["schedule_router", "settings_router"]
