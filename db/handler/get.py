import math
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import joinedload, aliased
from db.models import Activity, Building, org_activity, Organization, OrganizationPhone

# --------------------------
# Helper: сериализация ORM
# --------------------------
def serialize_organization(org: Organization):
    return {
        "id": org.id,
        "name": org.name,
        "building": {
            "id": org.building.id,
            "address": org.building.address,
            "latitude": org.building.latitude,
            "longitude": org.building.longitude,
        } if org.building else None,
        "phones": [p.phone for p in org.phones],
        "activities": [a.name for a in org.activities],
    }

# --------------------------
# Простые хэндлеры
# --------------------------
async def get_organizations_handler(session: AsyncSession):
    result = await session.execute(
        select(Organization)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.activities),
        )
    )
    return [serialize_organization(org) for org in result.unique().scalars().all()]


async def get_organization_by_id_handler(organization_id: int, session: AsyncSession):
    result = await session.execute(
        select(Organization)
        .where(Organization.id == organization_id)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.activities),
        )
    )
    org = result.unique().scalars().one_or_none()
    return serialize_organization(org) if org else None


async def search_organizations_handler(name: str, session: AsyncSession):
    result = await session.execute(
        select(Organization)
        .where(Organization.name.ilike(f"%{name}%"))
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.activities),
        )
    )
    return [serialize_organization(org) for org in result.unique().scalars().all()]


async def get_organizations_by_building_id_handler(building_id: int, session: AsyncSession):
    result = await session.execute(
        select(Organization)
        .where(Organization.building_id == building_id)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.activities),
        )
    )
    return [serialize_organization(org) for org in result.scalars().all()]


# --------------------------
# Поиск организаций по деятельности (рекурсивное дерево)
# --------------------------
async def get_organizations_by_activity_id_handler(activity_id: int, session: AsyncSession):
    result = await session.execute(
        select(Activity).where(Activity.id == activity_id, Activity.parent_id == None)
    )
    root_activity = result.unique().scalars().one_or_none()
    if not root_activity:
        return []

    # Рекурсивное CTE для всех потомков
    activity_cte = select(Activity.id).where(Activity.id == root_activity.id).cte(name="activity_tree", recursive=True)
    activity_cte = activity_cte.union_all(
        select(Activity.id).where(Activity.parent_id == activity_cte.c.id)
    )

    orgs_query = (
        select(Organization)
        .join(org_activity, Organization.id == org_activity.c.organization_id)
        .join(activity_cte, org_activity.c.activity_id == activity_cte.c.id)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.activities),
        )
        .distinct()
    )

    result = await session.execute(orgs_query)
    organizations = result.scalars().all()
    return [serialize_organization(org) for org in organizations]


async def get_organizations_by_activity_tree_handler(activity_name: str, session: AsyncSession):
    result = await session.execute(
        select(Activity).where(Activity.name == activity_name, Activity.parent_id == None)
    )
    root_activity = result.unique().scalars().one_or_none()
    if not root_activity:
        return []

    # Рекурсивное CTE
    activity_cte = select(Activity.id).where(Activity.id == root_activity.id).cte(name="activity_tree", recursive=True)
    activity_cte = activity_cte.union_all(
        select(Activity.id).where(Activity.parent_id == activity_cte.c.id)
    )

    orgs_query = (
        select(Organization)
        .join(org_activity, Organization.id == org_activity.c.organization_id)
        .join(activity_cte, org_activity.c.activity_id == activity_cte.c.id)
        .options(
            joinedload(Organization.building),
            joinedload(Organization.phones),
            joinedload(Organization.activities),
        )
        .distinct()
    )

    result = await session.execute(orgs_query)
    organizations = result.unique().scalars().all()
    return [serialize_organization(org) for org in organizations]


# --------------------------
# Поиск организаций на площади или в радиусе
# --------------------------
async def get_organizations_nearby_handler(
    lat: float,
    lon: float,
    session: AsyncSession,
    radius: float = None,
    min_lat: float = None,
    max_lat: float = None,
    min_lon: float = None,
    max_lon: float = None,
):
    q = select(Organization).join(Building, Organization.building_id == Building.id).options(
        joinedload(Organization.building),
        joinedload(Organization.phones),
        joinedload(Organization.activities),
    )

    # Прямоугольная область
    if None not in (min_lat, max_lat, min_lon, max_lon):
        q = q.where(
            and_(
                Building.latitude >= min_lat,
                Building.latitude <= max_lat,
                Building.longitude >= min_lon,
                Building.longitude <= max_lon,
            )
        )
        result = await session.execute(q)
        organizations = result.unique().scalars().all()
        return [serialize_organization(org) for org in organizations]

    # Радиус
    elif radius is not None:
        earth_radius_km = 6371.0
        delta_deg_lat = radius / 111.0
        delta_deg_lon = radius / (111.320 * math.cos(math.radians(lat)))
        bbox_min_lat = lat - delta_deg_lat
        bbox_max_lat = lat + delta_deg_lat
        bbox_min_lon = lon - delta_deg_lon
        bbox_max_lon = lon + delta_deg_lon

        q = q.where(
            and_(
                Building.latitude >= bbox_min_lat,
                Building.latitude <= bbox_max_lat,
                Building.longitude >= bbox_min_lon,
                Building.longitude <= bbox_max_lon,
            )
        )
        result = await session.execute(q)
        candidates = result.unique().scalars().all()

        def haversine(lat1, lon1, lat2, lon2):
            R = 6371.0
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            d_phi = math.radians(lat2 - lat1)
            d_lambda = math.radians(lon2 - lon1)
            a = (
                math.sin(d_phi / 2) ** 2
                + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
            )
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        organizations = [
            org for org in candidates
            if haversine(lat, lon, org.building.latitude, org.building.longitude) <= radius
        ]
        return [serialize_organization(org) for org in organizations]

    # Все организации, если не указано ни радиус, ни прямоугольник
    else:
        result = await session.execute(q)
        organizations = result.unique().scalars().all()
        return [serialize_organization(org) for org in organizations]


# --------------------------
# Остальные сущности
# --------------------------
async def get_phones_by_organization_handler(organization_id: int, session: AsyncSession):
    result = await session.execute(
        select(OrganizationPhone).where(OrganizationPhone.organization_id == organization_id)
    )
    return [p.phone for p in result.unique().scalars().all()]


async def get_buildings_handler(session: AsyncSession):
    result = await session.execute(select(Building))
    return result.unique().scalars().all()


async def get_building_by_id_handler(building_id: int, session: AsyncSession):
    result = await session.execute(select(Building).where(Building.id == building_id))
    return result.unique().scalars().one_or_none()


async def get_activities_handler(session: AsyncSession):
    result = await session.execute(select(Activity))
    return result.unique().scalars().all()


async def get_activity_by_id_handler(activity_id: int, session: AsyncSession):
    result = await session.execute(select(Activity).where(Activity.id == activity_id))
    return result.unique().scalars().one_or_none()
