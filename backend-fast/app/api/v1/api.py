from fastapi import APIRouter
from .endpoints import auth, projects, formats, generation, admin, users, monitoring, assets, analytics, organization_settings

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(projects.router, prefix="/projects", tags=["Projects & Assets"])
api_router.include_router(formats.router, prefix="/formats", tags=["User - Formats"])
api_router.include_router(generation.router, prefix="/generate", tags=["Generation"])
api_router.include_router(organization_settings.router, prefix="/settings", tags=["Organization Settings"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(monitoring.router, prefix="/monitoring", tags=["Monitoring"])
api_router.include_router(assets.router, prefix="/assets", tags=["Assets"])
api_router.include_router(analytics.router, prefix="/admin/analytics", tags=["Analytics"])
