from sqlalchemy import (
    Column, Integer, String, Float, ForeignKey, Table, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Таблица связи многие-ко-многим: Организации ↔ Деятельности
org_activity = Table(
    "org_activity", Base.metadata,
    Column("organization_id", Integer, ForeignKey("organizations.id", ondelete="CASCADE"), primary_key=True),
    Column("activity_id", Integer, ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
)

class Building(Base):
    __tablename__ = "buildings"

    id = Column(Integer, primary_key=True)
    address = Column(String(255), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

    organizations = relationship("Organization", back_populates="building")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True)
    name = Column(String(200), nullable=False, unique=True)
    parent_id = Column(Integer, ForeignKey("activities.id", ondelete="SET NULL"), nullable=True)

    parent = relationship("Activity", remote_side=[id], backref="children")

class OrganizationPhone(Base):
    __tablename__ = "organization_phones"

    id = Column(Integer, primary_key=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    phone = Column(String(50), nullable=False)

class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    building_id = Column(Integer, ForeignKey("buildings.id", ondelete="RESTRICT"), nullable=False)

    building = relationship("Building", back_populates="organizations")
    phones = relationship("OrganizationPhone", cascade="all, delete-orphan")
    activities = relationship("Activity", secondary=org_activity, backref="organizations")

    __table_args__ = (
        UniqueConstraint("name", "building_id", name="uix_name_building"),
    )