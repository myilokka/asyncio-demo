import os
from enum import Enum
from sqlalchemy import Integer, String, Enum as SqlAlchemyEnum
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from pydantic_settings import BaseSettings, SettingsConfigDict


class DbSettings(BaseSettings):
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    def get_db_url(self):
        return f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'

    model_config = SettingsConfigDict(env_file='.env')


db_settings = DbSettings()

PG_DSN = db_settings.get_db_url()
engine = create_async_engine(PG_DSN)
SessionDB = async_sessionmaker(bind=engine, expire_on_commit=False)


class Base(DeclarativeBase, AsyncAttrs):
    pass



class SwapiPeople(Base):
    __tablename__ = "swapi_people"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    birth_year: Mapped[str] = mapped_column(String(20), nullable=True)
    eye_color: Mapped[str] = mapped_column(String(60), nullable=True)
    films: Mapped[str] = mapped_column(String, nullable=True)
    gender: Mapped[str] = mapped_column(String(60), nullable=True)
    hair_color: Mapped[str] = mapped_column(String(60), nullable=True)
    height: Mapped[str] = mapped_column(String(20), nullable=True)
    homeworld: Mapped[str] = mapped_column(String, nullable=True)
    mass: Mapped[str] = mapped_column(String(20), nullable=True)
    name: Mapped[str] = mapped_column(String(255), nullable=True)
    skin_color: Mapped[str] = mapped_column(String(60), nullable=True)
    species: Mapped[str] = mapped_column(String, nullable=True)
    starships: Mapped[str] = mapped_column(String, nullable=True)
    vehicles: Mapped[str] = mapped_column(String, nullable=True)


async def init_orm():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
