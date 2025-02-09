from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

from sqlmodel import Session, SQLModel, create_engine, select

from src import config
from src.models import NotificationModel, UserModel

if TYPE_CHECKING:
    from collections.abc import Sequence

ModelT = TypeVar("ModelT", bound=SQLModel)


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

    @classmethod
    def update_user_id(cls, user: UserModel, new_id: int) -> UserModel:
        with Session(cls._engine) as session:
            notifications: Sequence[NotificationModel] = session.exec(
                select(NotificationModel).where(NotificationModel.user_id == user.id)
            ).all()

            user.id = new_id
            for notification in notifications:
                notification.user_id = new_id
                session.commit()

            return cls._update(session, user)
