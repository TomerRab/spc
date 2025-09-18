from fastapi import APIRouter
from .auth_routes import router as auth_router
from .groups_routes import router as groups_router  
from .projects_routes import router as projects_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(groups_router)
router.include_router(projects_router)