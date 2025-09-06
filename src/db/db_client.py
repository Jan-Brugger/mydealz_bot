from __future__ import annotations

import logging
from typing import TypeVar

from sqlmodel import Session, SQLModel, create_engine

from src import config

ModelT = TypeVar("ModelT", bound=SQLModel)

logger = logging.getLogger(__name__)


class DbClient:
    _engine = create_engine(f"sqlite:///{config.DATABASE}")

    @classmethod
    def init_db(cls) -> None:
        import src.models  # noqa: F401, PLC0415

        SQLModel.metadata.create_all(cls._engine)

    @classmethod
    def add(cls, model: ModelT) -> ModelT:
        with Session(cls._engine) as session:
            session.add(model)
            session.commit()
            session.refresh(model)
            session.expunge(model)

            return model

    @classmethod
    def _update(cls, session: Session, model: ModelT) -> ModelT:
        session.add(model)
        session.commit()
        session.refresh(model)

        return model

    @classmethod
    def _delete(cls, session: Session, instance: object) -> None:
        session.delete(instance)
        session.commit()
