import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from sqlalchemy import text

load_dotenv()

from db.models import Base, Building, Activity, Organization, OrganizationPhone

# ⚙️ Настройка подключения
DATABASE_URL = os.getenv("DATABASE_URL")
print(DATABASE_URL)
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def seed_data():
    async with AsyncSessionLocal() as session:
        # Очистим таблицы
        await session.execute(text("DELETE FROM organization_phones"))
        await session.execute(text("DELETE FROM org_activity"))
        await session.execute(text("DELETE FROM organizations"))
        await session.execute(text("DELETE FROM activities"))
        await session.execute(text("DELETE FROM buildings"))

        # --- Здания (с координатами, чтобы протестировать поиск по радиусу) ---
        b1 = Building(address="г. Москва, ул. Ленина 1", latitude=55.7558, longitude=37.6173)   # центр Москвы
        b2 = Building(address="г. Москва, пр-т Вернадского 78", latitude=55.6761, longitude=37.5066)  # юго-запад Москвы
        b3 = Building(address="г. Мытищи, ул. Сукромка 5", latitude=55.9117, longitude=37.7302)  # за пределами Москвы
        b4 = Building(address="г. Казань, ул. Баумана 10", latitude=55.7963, longitude=49.1088)  # другой город
        session.add_all([b1, b2, b3, b4])

        # --- Деятельности ---
        food = Activity(name="Еда")
        meat = Activity(name="Мясная продукция", parent=food)
        milk = Activity(name="Молочная продукция", parent=food)

        auto = Activity(name="Автомобили")
        cars = Activity(name="Легковые", parent=auto)
        trucks = Activity(name="Грузовые", parent=auto)
        session.add_all([food, meat, milk, auto, cars, trucks])

        # --- Организации ---
        org1 = Organization(name="ООО Рога и Копыта", building=b1)
        org2 = Organization(name="ИП Молочные продукты", building=b2)
        org3 = Organization(name="Мясокомбинат Мытищинский", building=b3)
        org4 = Organization(name="Автоцентр Казань", building=b4)

        org1.phones = [OrganizationPhone(phone="8-923-666-13-13")]
        org2.phones = [OrganizationPhone(phone="8-800-333-55-22")]
        org3.phones = [OrganizationPhone(phone="8-495-555-55-55")]
        org4.phones = [OrganizationPhone(phone="8-843-100-00-00")]

        # Связи организация ↔ деятельность
        org1.activities = [meat]
        org2.activities = [milk]
        org3.activities = [meat, milk]
        org4.activities = [cars]

        session.add_all([org1, org2, org3, org4])
        await session.commit()
        print("✅ Тестовые данные с координатами успешно добавлены.")


if __name__ == "__main__":
    asyncio.run(seed_data())
