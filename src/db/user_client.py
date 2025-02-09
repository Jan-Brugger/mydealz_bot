from __future__ import annotations

from sqlmodel import Session, select

from src.db.db_client import DbClient
from src.exceptions import UserNotFoundError
from src.models import UserModel


class UserClient(DbClient):
    @classmethod
    def fetch(cls, user_id: int) -> UserModel:
        with Session(cls._engine) as session:
            return cls._fetch(session, user_id)

    @classmethod
    def fetch_all_ids(cls) -> list[int]:
        with Session(cls._engine) as session:
            statement = select(UserModel)

            return [user.id for user in session.exec(statement).all()]

    @classmethod
    def disable(cls, user_id: int) -> UserModel:
        with Session(cls._engine) as session:
            user = cls._fetch(session, user_id)
            user.active = False
            return cls._update(session, user)

    @classmethod
    def enable(cls, user_id: int) -> UserModel:
        with Session(cls._engine) as session:
            user = cls._fetch(session, user_id)
            user.active = True
            return cls._update(session, user)

    @classmethod
    def _fetch(cls, session: Session, user_id: int) -> UserModel:
        statement = select(UserModel).where(UserModel.id == user_id)
        result: UserModel | None = session.exec(statement).first()

        if not result:
            raise UserNotFoundError(user_id)

        return result

    @classmethod
    def delete(cls, user_id: int) -> None:
        with Session(cls._engine) as session:
            user = cls._fetch(session, user_id)
            cls._delete(session, user)

    @classmethod
    def toggle_search_mydealz(cls, user_id: int) -> UserModel:
        with Session(cls._engine) as session:
            user = cls._fetch(session, user_id)
            user.search_mydealz = not user.search_mydealz

            return cls._update(session, user)

    @classmethod
    def toggle_search_preisjaeger(cls, user_id: int) -> UserModel:
        with Session(cls._engine) as session:
            user = cls._fetch(session, user_id)
            user.search_preisjaeger = not user.search_preisjaeger

            return cls._update(session, user)

    @classmethod
    def toggle_send_images(cls, user_id: int) -> UserModel:
        with Session(cls._engine) as session:
            user = cls._fetch(session, user_id)
            user.send_images = not user.send_images

            return cls._update(session, user)
