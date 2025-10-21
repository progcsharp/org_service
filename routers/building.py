from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import get_db
from db.handler.get import get_buildings_handler, get_building_by_id_handler
from db.handler.create import create_building_handler
from db.handler.update import update_building_handler
from db.handler.delete import delete_building_handler
from shemas.building import BuildingCreate, BuildingUpdate

router = APIRouter(prefix="/buildings", tags=["buildings"])

@router.get("/")
async def get_buildings(db: AsyncSession = Depends(get_db)):
    async with db() as session:
        buildings = await get_buildings_handler(session)
    return buildings


@router.get("/{building_id}")
async def get_building(building_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        building = await get_building_by_id_handler(building_id, session)
    return building


@router.post("/")
async def create_building(building: BuildingCreate, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        building = await create_building_handler(building.address, building.latitude, building.longitude, session)
    return building


@router.put("/{building_id}")
async def update_building(building_id: int, building: BuildingUpdate, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        building = await update_building_handler(building_id, building.address, building.latitude, building.longitude, session)
    return building


@router.delete("/{building_id}")
async def delete_building(building_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        building = await delete_building_handler(building_id, session)
    return building