import uuid
from enum import Enum
from sqlmodel import SQLModel, Field

class Difficulty(Enum):
    Easy = 0
    Hard = 1

class Team(SQLModel, table = True):
    uuid: str = Field(default_factory = lambda: str(uuid.uuid4()), primary_key = True)
    name: str = Field(unique = True)
    difficulty: int
    currentLevel: int = Field(default = 1, min = 1)

    def getDifficulty(self):
        return Difficulty(self.difficulty)

    def getLastLevel(self):
        return 6 if self.getDifficulty() == Difficulty.Easy else 8