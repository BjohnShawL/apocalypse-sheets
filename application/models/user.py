from uuid import UUID
from pydantic.dataclasses import dataclass
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .model import BaseModel
from application.extensions import db

class User(BaseModel):
    __tablename__ = 'users'

    username :Mapped[str] = mapped_column(db.String(256))
    email :Mapped[str] = mapped_column(db.String(256))
    password :Mapped[str] = mapped_column(db.String(256))

    def __init__(self, username, email, password):

        super().__init__()
        self.username = username
        self.email = email
        self.password = password



@dataclass
class UserItem:
    username : str
    email : str
    user_id:str

    @staticmethod
    def from_alchemy(alchemy_item: User):
        return UserItem(alchemy_item.username, alchemy_item.email, str(alchemy_item.id))