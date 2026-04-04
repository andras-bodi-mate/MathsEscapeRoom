from typing import Optional

from pydantic import BaseModel

from enums import (
    AccessQueryPath,
    Difficulty,
    GameStatus
)

class AccessQuery(BaseModel):
    path: AccessQueryPath
    level: Optional[int]

class Answer(BaseModel):
    level: int
    answer: int

class ExerciseQuery(BaseModel):
    level: int

class TeamNameAvailabilityQuery(BaseModel):
    teamName: str

class TeamRegistrationInfo(BaseModel):
    teamName: str
    difficulty: Difficulty

class TeamDeletionInfo(BaseModel):
    teamUuid: str

class TeamModificationInfo(BaseModel):
    teamUuid: str
    newTeamName: str
    newDifficulty: Difficulty
    newLevel: int

class ExerciseDeletionInfo(BaseModel):
    level: int

class ExerciseModificationInfo(BaseModel):
    level: int
    newLevel: int
    newTitle: str
    newSolution: int

class GameControlInfo(BaseModel):
    newStatus: GameStatus