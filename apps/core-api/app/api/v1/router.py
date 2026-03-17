"""V1 API router — aggregates all v1 routes."""

from fastapi import APIRouter

from app.api.v1.a2a import router as a2a_router
from app.api.v1.admin import router as admin_router
from app.api.v1.applications import router as applications_router
from app.api.v1.auth import router as auth_router
from app.api.v1.credentials import router as credentials_router
from app.api.v1.drafts import router as drafts_router
from app.api.v1.events import router as events_router
from app.api.v1.evidence import router as evidence_router
from app.api.v1.graph import router as graph_router
from app.api.v1.me import router as me_router
from app.api.v1.projects import router as projects_router
from app.api.v1.quotas import router as quotas_router
from app.api.v1.reviews import router as reviews_router
from app.api.v1.rules import router as rules_router
from app.api.v1.sources import router as sources_router
from app.api.v1.sponsors import router as sponsors_router
from app.api.v1.tasks import router as tasks_router
from app.api.v1.webhooks import router as webhooks_router
from app.api.v1.work_packages import router as wp_router
from app.api.v1.workflows import router as workflows_router

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(admin_router)
v1_router.include_router(auth_router)
v1_router.include_router(me_router)
v1_router.include_router(projects_router)
v1_router.include_router(wp_router)
v1_router.include_router(tasks_router)
v1_router.include_router(applications_router)
v1_router.include_router(drafts_router)
v1_router.include_router(workflows_router)
v1_router.include_router(events_router)
v1_router.include_router(graph_router)
v1_router.include_router(rules_router)
v1_router.include_router(sources_router)
v1_router.include_router(webhooks_router)
v1_router.include_router(reviews_router)
v1_router.include_router(sponsors_router)
v1_router.include_router(quotas_router)
v1_router.include_router(credentials_router)
v1_router.include_router(evidence_router)
v1_router.include_router(a2a_router)
