import uuid
from enum import Enum

class Difficulty(Enum):
    Easy = 0
    Hard = 1

class Team:
    uuidTeamMap: dict[str, "Team"] = {}

    def __init__(self, name: str, difficulty: Difficulty):
        self.uuid = str(uuid.uuid4())
        self.name = name
        self.difficulty = difficulty
        self.currentLevel = 1

        Team.uuidTeamMap[self.uuid] = self