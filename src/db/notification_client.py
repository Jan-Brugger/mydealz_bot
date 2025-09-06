from __future__ import annotations

from sqlmodel import Session, select

from src.db.db_client import DbClient
from src.exceptions import NotificationNotFoundError
from src.models import NotificationModel, UserModel


class NotificationClient(DbClient):
    @classmethod
    def fetch(cls, notification_id: int) -> NotificationModel:
        with Session(cls._engine) as session:
            notification = cls._fetch(session, notification_id)

            if not notification:
                raise NotificationNotFoundError(notification_id)

            return notification

    @classmethod
    def fetch_all_active(cls) -> list[tuple[NotificationModel, UserModel]]:
        with Session(cls._engine) as session:
            statement = (
                select(NotificationModel, UserModel)
                .where(NotificationModel.user_id == UserModel.id)
                .where(UserModel.active == True)  # noqa: E712
            )

            return [(r[0], r[1]) for r in session.exec(statement).all()]

    @classmethod
    def fetch_by_user_id(cls, user_id: int) -> list[NotificationModel]:
        with Session(cls._engine) as session:
            statement = select(NotificationModel).where(NotificationModel.user_id == user_id)

            return list(session.exec(statement).all())

    @classmethod
    def _fetch(cls, session: Session, notification_id: int) -> NotificationModel:
        statement = select(NotificationModel).where(NotificationModel.id == notification_id)

        notification: NotificationModel | None = session.exec(statement).first()

        if not notification:
            raise NotificationNotFoundError(notification_id)

        return notification

    @classmethod
    def delete(cls, notification_id: int) -> NotificationModel:
        with Session(cls._engine) as session:
            notification = cls._fetch(session, notification_id)
            cls._delete(session, notification)

            return notification

    @classmethod
    def update_query(cls, notification_id: int, new_query: str) -> NotificationModel:
        with Session(cls._engine) as session:
            notification = cls._fetch(session, notification_id)
            notification.search_query = new_query
            return cls._update(session, notification)

    @classmethod
    def update_min_price(cls, notification_id: int, new_min_price: int) -> NotificationModel:
        with Session(cls._engine) as session:
            notification = cls._fetch(session, notification_id)
            notification.min_price = new_min_price
            return cls._update(session, notification)

    @classmethod
    def update_max_price(cls, notification_id: int, new_max_price: int) -> NotificationModel:
        with Session(cls._engine) as session:
            notification = cls._fetch(session, notification_id)
            notification.max_price = new_max_price
            return cls._update(session, notification)

    @classmethod
    def toggle_search_hot_only(cls, notification_id: int) -> NotificationModel:
        with Session(cls._engine) as session:
            notification = cls._fetch(session, notification_id)
            notification.search_hot_only = not notification.search_hot_only
            return cls._update(session, notification)

    @classmethod
    def toggle_search_description(cls, notification_id: int) -> NotificationModel:
        with Session(cls._engine) as session:
            notification = cls._fetch(session, notification_id)
            notification.search_description = not notification.search_description
            return cls._update(session, notification)

    @classmethod
    def update_user_id(cls, old_user_id: int, new_user_id: int) -> None:
        notifications = cls.fetch_by_user_id(old_user_id)

        with Session(cls._engine) as session:
            for notification in notifications:
                notification.user_id = new_user_id
                cls._update(session, notification)
