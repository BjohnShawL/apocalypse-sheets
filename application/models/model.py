from typing import Any, Optional
import uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Boolean, String
from pydantic.dataclasses import dataclass

class BaseModel(DeclarativeBase):
    id:Mapped[str] = mapped_column(String(32), primary_key=True)
    def __init__(self, **kw: Any):
        super().__init__()
        self.id = uuid.uuid4().hex

@dataclass
class MenuItem:
    """
    name, is_category_item, url, items
    """
    name: str
    is_category_item: bool
    url:str
    items: Optional[list["MenuItem"]] = None
    subitem_names: Optional[list[str]] = None