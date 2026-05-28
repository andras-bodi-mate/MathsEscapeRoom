import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, DateTime
from sqlmodel import SQLModel, Field

from src.enums import Difficulty, GameStatus

class Exercise(SQLModel, table = True):
    __tablename__ = "Exercises"
    level: int = Field(primary_key = True)
    title: str = Field(nullable = False)
    solution: int = Field(nullable = False)

class Team(SQLModel, table = True):
    __tablename__ = "Teams"
    uuid: str = Field(default_factory = lambda: str(uuid.uuid4()), primary_key = True)
    name: str = Field(unique = True)
    difficulty: int = Field(nullable = False)
    currentLevel: int = Field(default = 1, nullable = False)
    registrationTime: str = Field(
        default_factory = lambda: datetime.now(timezone.utc).isoformat(),
        nullable = True
    )

    def getDifficulty(self):
        return Difficulty(self.difficulty)

    def getLastLevel(self):
        return 6 if self.getDifficulty() == Difficulty.Easy else 8
    
class GameState(SQLModel, table = True):
    __tablename__ = "GameState"
    id: int = Field(default = 1, primary_key = True)
    status: int = Field(default = GameStatus.Stopped.value)