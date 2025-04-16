from typing import Final, Any
from uuid import UUID

from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy.ext.associationproxy import AssociationProxy
from application.extensions import db

from .model import BaseModel


class Tag(BaseModel):
    __tablename__ = 'tags'
    name: Mapped[str] = mapped_column(db.String(256))

    def __init__(self, name: str, **kw: Any):
        super().__init__(**kw)
        self.name = name


class Item(BaseModel):
    __tablename__ = 'items'
    name: Mapped[str] = mapped_column(db.String(256))
    tags: Mapped[list[Tag]] = relationship(secondary=lambda: item_to_tags_table)

    def __init__(self, name: str, **kw: Any):
        super().__init__(**kw)
        self.name = name

    tag_association: AssociationProxy[list[str]] = association_proxy("tags", "name")


item_to_tags_table: Final[Table] = Table(
    'item_to_tags', BaseModel.metadata, Column('item_id', db.String(32), ForeignKey('items.id'), primary_key=True),
    Column('tag_id', db.String(32), ForeignKey('tags.id'), primary_key=True)
)

# class ItemToTag(BaseModel):
#     __tablename__ = 'items_to_tags'
#     id: Mapped[UUID] = mapped_column(db.UUID, primary_key=True)
#     score: Mapped[int] = mapped_column(db.Integer)
#     item_id: Mapped[UUID] = mapped_column(db.UUID, db.ForeignKey('items.id'))
#     tag_id: Mapped[UUID] = mapped_column(db.UUID, db.ForeignKey('tags.id'))
