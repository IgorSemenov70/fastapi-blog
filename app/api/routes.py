from fastapi import APIRouter

from app.api.authentication.endpoints import auth_router
from app.api.posts.endpoints import post_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["Auth"])
router.include_router(post_router, prefix="/posts", tags=["Posts"])
