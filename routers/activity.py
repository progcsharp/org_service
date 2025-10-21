from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import get_db
from db.handler.get import get_activities_handler, get_activity_by_id_handler
from db.handler.create import create_activity_handler
from db.handler.update import update_activity_handler
from db.handler.delete import delete_activity_handler
from shemas.activity import ActivityCreate, ActivityUpdate

router = APIRouter(prefix="/activities", tags=["activities"])

@router.get("/")
async def get_activities(db: AsyncSession = Depends(get_db)):
    async with db() as session:
        activities = await get_activities_handler(session)
    return activities


@router.get("/{activity_id}")
async def get_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        activity = await get_activity_by_id_handler(activity_id, session)
    return activity


@router.post("/")
async def create_activity(activity: ActivityCreate, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        activity = await create_activity_handler(activity.name, activity.parent_id, session)
    return activity


@router.put("/{activity_id}")
async def update_activity(activity_id: int, activity: ActivityUpdate, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        activity = await update_activity_handler(activity_id, activity.name, activity.parent_id, session)
    return activity


@router.delete("/{activity_id}")
async def delete_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        activity = await delete_activity_handler(activity_id, session)
    return activity