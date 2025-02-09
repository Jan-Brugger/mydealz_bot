import pytest
from sqlalchemy import inspect
from sqlmodel import Session, select

from src.db.db_client import DbClient
from src.db.notification_client import NotificationClient
from src.db.user_client import UserClient
from src.exceptions import NotificationNotFoundError
from src.models import NotificationModel, UserModel


class TestDbCore:
    @classmethod
    def test_init(cls, db_client: DbClient) -> None:
        db_client.init_db()
        assert inspect(db_client._engine).has_table("users")
        assert inspect(db_client._engine).has_table("notifications")

    @classmethod
    def test_db_add(
        cls,
        users: tuple[UserModel, ...],
        all_notifications: tuple[NotificationModel, ...],
        session: Session,
    ) -> None:
        for user in users:
            UserClient.add(user)

        for notification in all_notifications:
            NotificationClient().add(notification)

        assert len(session.exec(select(UserModel)).all()) == len(users)
        assert len(session.exec(select(NotificationModel)).all()) == len(all_notifications)

    @classmethod
    def test_db_fetch_single(
        cls,
        user0: UserModel,
        notification1: NotificationModel,
    ) -> None:
        db_user = UserClient.fetch(user0.id)
        assert isinstance(db_user, UserModel)
        assert dict(db_user) == dict(user0)

        db_notification = NotificationClient().fetch(notification1.id)
        assert isinstance(db_notification, NotificationModel)
        assert dict(db_notification) == dict(notification1)

    @classmethod
    def test_db_client_fetch_multi(cls, active_notifications: tuple[NotificationModel, ...], user0: UserModel) -> None:
        db_notifications = NotificationClient().fetch_all_active()
        assert len(db_notifications) == len(active_notifications)
        assert dict(db_notifications[1][0]) == dict(active_notifications[1])
        assert dict(db_notifications[1][1]) == dict(user0)

    @classmethod
    def test_fetch_notifications_by_user_id(
        cls, user0: UserModel, all_notifications: tuple[NotificationModel, ...]
    ) -> None:
        db_notifications = NotificationClient().fetch_by_user_id(user0.id)
        assert len(db_notifications) == len(
            [notification for notification in all_notifications if notification.user_id == user0.id]
        )

    @classmethod
    def test_db_update_update_user_active(cls) -> None:
        assert UserClient.fetch(1).active is True
        UserClient.disable(1)
        assert UserClient.fetch(1).active is False
        UserClient.enable(1)
        assert UserClient.fetch(1).active is True

    @classmethod
    def test_delete(cls, notification1: NotificationModel) -> None:
        notification_client = NotificationClient()
        assert isinstance(notification_client.fetch(notification1.id), NotificationModel)
        notification_client.delete(notification1.id)
        with pytest.raises(NotificationNotFoundError):
            notification_client.fetch(notification1.id)

    @classmethod
    def test_change_user_id(
        cls,
        user1: UserModel,
    ) -> None:
        updated_user = DbClient.update_user_id(user1, 30)
        fetched_user = UserClient.fetch(30)
        notifications = NotificationClient.fetch_by_user_id(30)

        assert updated_user == fetched_user
        assert len(notifications) > 0
        assert isinstance(notifications[0], NotificationModel)
