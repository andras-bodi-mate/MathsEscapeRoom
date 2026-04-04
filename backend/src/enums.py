from enum import IntEnum, unique

@unique
class AnswerResponse(IntEnum):
    Wrong = 0
    Correct = 1
    Finished = 2

@unique
class AccessQueryPath(IntEnum):
    Exercise: 0
    Results: 1

@unique
class Difficulty(IntEnum):
    Easy = 0
    Hard = 1

@unique
class GameStatus(IntEnum):
    Stopped = 0
    Started = 1
