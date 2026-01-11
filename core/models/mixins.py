from sqlalchemy import ForeignKey
from sqlalchemy.orm import declared_attr, Mapped, mapped_column, relationship

from core.models.users import User


class UserRelationship:
    _user_back_populates = ""

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(
            ForeignKey("users.id"),
            nullable=False,
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        return relationship(back_populates=cls._user_back_populates)
