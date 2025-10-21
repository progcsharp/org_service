from sqlalchemy.ext.asyncio import AsyncSession
from db.models import Building, Activity
from sqlalchemy import select

async def update_building_handler(building_id: int, address: str, latitude: float, longitude: float, session: AsyncSession):
    building = await session.execute(select(Building).where(Building.id == building_id))
    building = building.scalar_one_or_none()
    if building:
        building.address = address
        building.latitude = latitude
        building.longitude = longitude
        await session.commit()
        return building


async def update_activity_handler(activity_id: int, name: str, parent_id: int | None, session: AsyncSession):
    activity = await session.execute(select(Activity).where(Activity.id == activity_id))
    activity = activity.scalar_one_or_none()
    if activity:
        activity.name = name
        activity.parent_id = parent_id
        await session.commit()
        return activity
    else:
        return None