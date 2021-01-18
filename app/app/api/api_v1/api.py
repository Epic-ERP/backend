from fastapi import APIRouter

from app.api.api_v1.endpoints import admins, login, schools, users, utils

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(admins.router, prefix="/admins", tags=["admins"])
api_router.include_router(schools.router, prefix="/schools", tags=["schools"])
