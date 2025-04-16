from typing import Optional, Final

from pydantic.dataclasses import dataclass
from sqlalchemy import Table, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship

from application.extensions import db
from .model import BaseModel
from .user import User


class Stat(BaseModel):
    __tablename__ = 'stats'
    name: Mapped[str] = mapped_column(db.String(100))
    score: Mapped[int] = mapped_column(db.Integer)
    character_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey('characters.id'), nullable=False)

    def __init__(self, name: str, score: int, character_id: str):
        super().__init__()
        self.name = name
        self.score = score
        self.character_id = character_id


class Move(BaseModel):
    __tablename__ = 'moves'
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[str] = mapped_column(db.String(512), nullable=False)
    playbook_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("playbooks.id"), nullable=False)
    owning_user_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("users.id"), nullable=False)

    def __init__(self, name, description, playbook_id, owning_user_id):
        super().__init__()
        self.name = name
        self.description = description
        self.playbook_id = playbook_id
        self.owning_user_id = owning_user_id



class Improvement(BaseModel):
    __tablename__ = 'improvements'
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    playbook_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("playbooks.id"), nullable=False)


class HistoryOption(BaseModel):
    __tablename__ = 'history_options'
    text: Mapped[str] = mapped_column(db.String(512), nullable=False)
    playbook_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("playbooks.id"), nullable=False)


class Playbook(BaseModel):
    """
    A class to represent a playbook. Playbooks have a name and a description,
    along with a list of moves, a list of history options, and a list of improvements.
    """
    __tablename__ = 'playbooks'
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[str] = mapped_column(db.String(512), nullable=False)
    owning_user_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("users.id"), nullable=False)
    moves: Mapped[list[Move]] = relationship("Move", backref="playbook")
    history_options: Mapped[list[HistoryOption]] = relationship("HistoryOption", backref="playbook")
    improvement_options: Mapped[list[Improvement]] = relationship("Improvement", backref="playbook")

    owning_user: Mapped[User] = relationship("User", backref="owned_playbooks")

    def __init__(self, name, description ):
        super().__init__()
        self.name = name
        self.description = description


class Character(BaseModel):
    """
    A class that represents a character. Characters have a name, stats, a single playbook,
    luck, harm and experience. They also have a relationship map and improvements, both of which
    pull their options from the playbook.
    
    """
    __tablename__ = 'characters'
    name: Mapped[str] = mapped_column(db.String(32), nullable=False)
    look: Mapped[str] = mapped_column(db.String(512), nullable=True)
    harm: Mapped[int] = mapped_column(db.Integer)
    experience: Mapped[int] = mapped_column(db.Integer)
    luck: Mapped[int] = mapped_column(db.Integer)
    playbook_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("playbooks.id"))
    user_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("users.id"))

    playbook: Mapped[Playbook] = relationship("Playbook")
    stats: Mapped[list[Stat]] = relationship("Stat", backref="character")
    user: Mapped[User] = relationship("User", backref="characters")
    relationship_map: dict[str, str] = {}
    selected_improvements: Mapped[list[Improvement]] = relationship(secondary=lambda: character_improvements_table)
    selected_moves: Mapped[list[Move]] = relationship(secondary=lambda: character_move_table)

    @property
    def stats_dict(self):
        stat_dict = {}
        if not self.stats:
            return stat_dict
        for stat in self.stats:
            stat_dict[stat.name.lower()] = stat.score
        return stat_dict

    def __init__(self, name, playbook_id: str, user_id: str):
        super().__init__()
        self.name = name
        self.playbook_id = playbook_id
        self.user_id = user_id
        self.harm = 0
        self.experience = 0
        self.luck = 0


character_move_table: Final[Table] = Table("character_to_moves_table", BaseModel.metadata,
                                           Column("character_id", db.String(32), db.ForeignKey("characters.id"),
                                                  primary_key=True),
                                           Column("move_id", db.String(32), db.ForeignKey("moves.id"),
                                                  primary_key=True))
character_improvements_table: Final[Table] = Table("character_to_improvements_table", BaseModel.metadata,
                                                   Column("character_id", db.String(32), db.ForeignKey("characters.id"),
                                                          primary_key=True),
                                                   Column("improvement_id", db.String(32),
                                                          db.ForeignKey("improvements.id"), primary_key=True))


class Party(BaseModel):
    __tablename__ = 'parties'
    name: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[str] = mapped_column(db.String(100), nullable=True)
    owner_id: Mapped[str] = mapped_column(db.String(32), db.ForeignKey("users.id"), nullable=False)

    players: Mapped[list[User]] = relationship(secondary=lambda: players_to_party_table)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


players_to_party_table: Final[Table] = Table(
    'players_to_party', BaseModel.metadata,
    Column('player_id', db.String(32), db.ForeignKey('users.id'), primary_key=True),
    Column('party_id', db.String(32), db.ForeignKey('parties.id'), primary_key=True), )


@dataclass
class CharacterItem:
    name: str
    playbook_name: str
    harm: int
    experience: int
    link: str

    @staticmethod
    def from_alchemy(alchemy_item: Character, link: Optional[str] = None) -> "CharacterItem":
        if not link:
            link = f"{alchemy_item.id}/edit"
        return CharacterItem(alchemy_item.name, alchemy_item.playbook.name, alchemy_item.harm, alchemy_item.experience,
                             link)

@dataclass
class PlaybookItem:
    name: str
    owner:str
    link: str

    @staticmethod
    def from_alchemy(alchemy_item: Playbook, link: Optional[str] = None) -> "PlaybookItem":

        if not link:
            link = f"list/{alchemy_item.id}/edit"
            return PlaybookItem(alchemy_item.name, alchemy_item.owning_user.username, link)