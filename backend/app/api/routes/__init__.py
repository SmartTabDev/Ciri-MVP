from fastapi import APIRouter

from app.api.routes import auth, users, ai, companies, ai_agent_settings, leads, analytics, company_context, notifications, instagram, facebook

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(companies.router, prefix="/companies", tags=["companies"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
api_router.include_router(ai_agent_settings.router, prefix="/ai-agent-settings", tags=["ai-agent-settings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(company_context.router, prefix="/company-context", tags=["company-context"])
api_router.include_router(notifications.router, prefix="/notifications", tags=["notifications"])
api_router.include_router(instagram.router, prefix="/instagram", tags=["instagram"])
api_router.include_router(facebook.router, prefix="/facebook", tags=["facebook"]) 