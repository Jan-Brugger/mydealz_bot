import pytest
from sqlalchemy import create_engine
from sqlmodel import Session

from src.db.db_client import DbClient
from src.models import NotificationModel, UserModel


@pytest.fixture
def user0() -> UserModel:
    return UserModel(
        id=1,
        username="john_doe",
        first_name="John",
        last_name="Doe",
        search_mydealz=True,
        search_preisjaeger=True,
        send_images=False,
        active=True,
    )


@pytest.fixture
def user1() -> UserModel:
    return UserModel(id=20, username="jane123", search_mydealz=False, search_preisjaeger=True)


@pytest.fixture
def users(user0: UserModel, user1: UserModel) -> tuple[UserModel, UserModel]:
    return user0, user1


@pytest.fixture
def notification0(user0: UserModel) -> NotificationModel:
    return NotificationModel(id=1, query="test query 1", user_id=user0.id)


@pytest.fixture
def notification1(user0: UserModel) -> NotificationModel:
    return NotificationModel(
        id=7,
        query="test query 2",
        user_id=user0.id,
        min_price=10,
        max_price=100,
        search_hot_only=True,
        search_description=True,
    )


@pytest.fixture
def notification2(user1: UserModel) -> NotificationModel:
    return NotificationModel(
        id=13,
        query="test query 3",
        user_id=user1.id,
        min_price=20,
        max_price=None,
        search_hot_only=False,
        search_description=True,
    )


@pytest.fixture
def notifications(
    notification0: NotificationModel,
    notification1: NotificationModel,
    notification2: NotificationModel,
) -> tuple[NotificationModel, NotificationModel, NotificationModel]:
    return notification0, notification1, notification2


@pytest.fixture(scope="class", autouse=True)
def db_client() -> DbClient:
    db_client = DbClient
    DbClient._engine = create_engine("sqlite:///:memory:", echo=False)

    return db_client()


@pytest.fixture(scope="class", autouse=True)
def session(db_client: DbClient) -> Session:
    return Session(db_client._engine)
