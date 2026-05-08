from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.tn import router as tn_router
from app.api.v1.stats import router as stats_router
from app.api.v1.search import router as search_router
from app.api.v1.blast import router as blast_router
from app.api.v1.minetn import router as minetn_router
from app.api.v1.admin import router as admin_router
from app.api.v1.classification import router as classification_router
from app.api.v1.user_admin import router as user_admin_router
from app.api.v1.review import router as review_router
from app.api.v1.export import router as export_router
from app.api.v1.analyze import router as analyze_router
from app.api.v1.import_tn import router as import_router
from app.api.v1.download_request import router as download_request_router
from app.api.v1.admin_settings import router as admin_settings_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(tn_router)
router.include_router(stats_router)
router.include_router(search_router)
router.include_router(blast_router)
router.include_router(minetn_router)
router.include_router(admin_router)
router.include_router(classification_router)
router.include_router(user_admin_router)
router.include_router(review_router)
router.include_router(export_router)
router.include_router(analyze_router)
router.include_router(import_router)
router.include_router(download_request_router)
router.include_router(admin_settings_router)

api_router = router
