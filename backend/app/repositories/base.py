import typing as tp

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_asyncio

from app.db import session as db_session

T = tp.TypeVar("T", bound=db_session.Base)


class BaseRepository(tp.Generic[T]):
    def __init__(self, model: tp.Type[T], db: sa_asyncio.AsyncSession):
        self.model = model
        self.db = db

    async def _scalar_one_or_none(self, stmt: sa.Select[tp.Any]) -> tp.Any:
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _scalars_all(self, stmt: sa.Select[tp.Any]) -> list[tp.Any]:
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, id: int) -> T | None:
        stmt = sa.select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        return tp.cast(T | None, await self._scalar_one_or_none(stmt))

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[T]:
        stmt = sa.select(self.model).offset(skip).limit(limit)
        return tp.cast(list[T], await self._scalars_all(stmt))

    async def get_by_ids(self, ids: list[int]) -> list[T]:
        if not ids:
            return []
        stmt = sa.select(self.model).where(self.model.id.in_(ids))  # type: ignore[attr-defined]
        return tp.cast(list[T], await self._scalars_all(stmt))

    async def create(self, obj_in: dict[str, tp.Any]) -> T:
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, id: int, obj_in: dict[str, tp.Any]) -> T | None:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return None
        for field, value in obj_in.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, id: int) -> bool:
        db_obj = await self.get_by_id(id)
        if not db_obj:
            return False
        await self.db.delete(db_obj)
        await self.db.commit()
        return True

    async def count(self) -> int:
        stmt = sa.select(sa.func.count()).select_from(self.model)
        result = await self.db.execute(stmt)
        return tp.cast(int, result.scalar_one())
