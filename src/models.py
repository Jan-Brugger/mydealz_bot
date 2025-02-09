from __future__ import annotations

import datetime  # noqa: TC003

from pydantic import BaseModel
from sqlmodel import Field, SQLModel

from src.queries import Queries


class UserModel(SQLModel, table=True):
    __tablename__ = "users"

    id: int = Field(primary_key=True)
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    search_mydealz: bool = True
    search_preisjaeger: bool = False
    send_images: bool = True
    active: bool = True


class NotificationModel(SQLModel, table=True):
    __tablename__ = "notifications"

    id: int = Field(default=None, primary_key=True)
    query: str
    min_price: int | None = None
    max_price: int | None = None
    search_hot_only: bool = False
    search_description: bool = False
    user_id: int = Field(foreign_key="users.id", ondelete="CASCADE")

    def __lt__(self, other: NotificationModel) -> bool:
        return self.query.lower() < other.query.lower()

    @property
    def queries(self) -> Queries:
        return Queries(self.query)


class PriceModel(BaseModel):
    amount: float
    currency: str = "€"


class DealModel(BaseModel):
    title: str
    description: str
    category: str
    merchant: str
    price: PriceModel
    link: str
    image_url: str
    published: datetime.datetime

    @property
    def full_title(self) -> str:
        if not self.merchant:
            return self.title

        title = self.title
        if title.lower().lstrip("[( ").startswith(self.merchant.lower()):
            title = title[title.lower().find(self.merchant.lower()) + len(self.merchant) :].lstrip(")] ")

        return f"[{self.merchant}] {title}"

    @property
    def search_title(self) -> str:
        return " ".join(self.full_title.lower().split())

    @property
    def search_title_and_description(self) -> str:
        return self.search_title + " ".join(self.description.lower().split())
