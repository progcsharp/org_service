from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.engine import get_db
from db.handler.get import (get_organizations_handler, get_organization_by_id_handler, search_organizations_handler, 
get_organizations_by_building_id_handler, get_organizations_by_activity_id_handler, get_organizations_by_activity_tree_handler,
get_organizations_nearby_handler, get_phones_by_organization_handler)
from db.handler.create import create_phone_handler
from db.handler.delete import delete_phone_handler

router = APIRouter(prefix="/organizations", tags=["organizations"])

@router.get("/")
async def get_organizations(db: AsyncSession = Depends(get_db)):
    async with db() as session:
        organizations = await get_organizations_handler(session)
    return organizations


@router.get("/search")
async def search_organizations(name: str, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        organizations = await search_organizations_handler(name, session)
    return organizations


@router.get("/nearby")
async def get_organizations_nearby(
    lat: float,
    lon: float,
    db: AsyncSession = Depends(get_db),
    radius: float = None,
    min_lat: float = None,
    max_lat: float = None,
    min_lon: float = None,
    max_lon: float = None
):
    async with db() as session:
        organizations = await get_organizations_nearby_handler(lat, lon, session, radius, min_lat, max_lat, min_lon, max_lon)
    return organizations


@router.get("/{organization_id}")
async def get_organization(organization_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        organization = await get_organization_by_id_handler(organization_id, session)
    return organization


@router.get("/by-building/{building_id}")
async def get_organizations_by_building(building_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        organizations = await get_organizations_by_building_id_handler(building_id, session)
    return organizations


@router.get("/by-activity/{activity_id}")
async def get_organizations_by_activity(activity_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        organizations = await get_organizations_by_activity_id_handler(activity_id, session)
    return organizations


@router.get("/by_activity_tree/{activity_name}")
async def get_organizations_by_activity_tree(activity_name: str, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        organizations = await get_organizations_by_activity_tree_handler(activity_name, session)
    return organizations


@router.get("/{organization_id}/phones")
async def get_phones_by_organization(organization_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        phones = await get_phones_by_organization_handler(organization_id, session)
    return phones


@router.post("/{organization_id}/phones")
async def create_phone(organization_id: int, phone: str, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        phone = await create_phone_handler(organization_id, phone, session)
    return phone


@router.delete("/{organization_id}/phones/{phone_id}")
async def delete_phone(organization_id: int, phone_id: int, db: AsyncSession = Depends(get_db)):
    async with db() as session:
        phone = await delete_phone_handler(organization_id, phone_id, session)
    return phone
