import datetime

import pgvector.sqlalchemy
from sqlalchemy import func, event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from app.settings import settings


class DbHelper:
    @staticmethod
    async def create_session_object():
        engine = create_async_engine(settings.DATABASE.POSTGRES_DSN.unicode_string())
        async_session = async_sessionmaker(
            engine,
            expire_on_commit=False,
            autoflush=False,
        )
        return async_session

    @staticmethod
    async def get_session() -> AsyncSession:
        async_session = await DbHelper.create_session_object()
        async with async_session() as session:
            yield session


class BaseModel(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    @declared_attr.directive
    def __tablename__(cls):
        return f"{cls.__name__.lower()}s"


@event.listens_for(BaseModel.metadata, 'column_reflect')
def receive_column_reflect(inspector, table, column_info):
    if column_info['type'] == 'pgvector':
        return pgvector.sqlalchemy.Vector()
