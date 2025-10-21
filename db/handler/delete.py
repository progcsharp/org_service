from sqlalchemy.ext.asyncio import AsyncSession
from db.models import OrganizationPhone, Building, Activity
from sqlalchemy import select

async def delete_phone_handler(organization_id: int, phone_id: int, session: AsyncSession):
    phone = await session.execute(select(OrganizationPhone).where(OrganizationPhone.id == phone_id, OrganizationPhone.organization_id == organization_id))
    phone.scalar_one_or_none()
    if phone:
        await session.delete(phone)
        await session.commit()
        return phone
    else:
        return None


async def delete_building_handler(building_id: int, session: AsyncSession):
    building = await session.execute(select(Building).where(Building.id == building_id))
    building = building.scalar_one_or_none()
    if building:
        await session.delete(building)
        await session.commit()
        return building
    else:
        return None


async def delete_activity_handler(activity_id: int, session: AsyncSession):
    activity = await session.execute(select(Activity).where(Activity.id == activity_id))
    activity = activity.scalar_one_or_none()
    if activity:
        await session.delete(activity)
        await session.commit()
        return activity
    else:
        return None