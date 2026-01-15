from .auth import router as auth_router
from .chat import router as chat_router
from .admin import router as admin_router
from .company import router as company_router
from .resource import router as resource_router

__all__ = [
    "auth_router",
    "chat_router",
    "admin_router",
    "company_router",
    "resource_router",
]

