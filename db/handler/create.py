from sqlalchemy.ext.asyncio import AsyncSession
from db.models import OrganizationPhone, Building, Activity

async def create_phone_handler(organization_id: int, phone: str, session: AsyncSession):

    phone = OrganizationPhone(organization_id=organization_id, phone=phone)
    session.add(phone)
    await session.commit()
    return phone    


async def create_building_handler(address: str, latitude: float, longitude: float, session: AsyncSession):
    building = Building(address=address, latitude=latitude, longitude=longitude)
    session.add(building)
    await session.commit()
    return building


async def create_activity_handler(name: str, parent_id: int | None, session: AsyncSession):
    activity = Activity(name=name, parent_id=parent_id)
    session.add(activity)
    await session.commit()
    return activity