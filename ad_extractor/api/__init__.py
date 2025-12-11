from fastapi import APIRouter
from api.ai_chat.views import router as ai_chat_router
from api.ad_extractor.views import router as ad_extractor_router
from api.evaluator.views import router as evaluator_router

router = APIRouter()

router.include_router(
    ad_extractor_router,
    prefix="/ad-extractor",
    tags=["AD Extractor"]
)
router.include_router(
    evaluator_router,
    prefix="/evaluator",
    tags=["Evaluator"]
)
router.include_router(
    ai_chat_router,
    prefix="/ai-chat",
    tags=["AI Chat"]
)