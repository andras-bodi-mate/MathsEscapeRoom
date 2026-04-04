from pathlib import Path

from sqlmodel import SQLModel, Session, create_engine, select, exists

from models import (
    Exercise,
    Team,
    GameState
)
from schemas import (
    Answer
)
from enums import (
    GameStatus
)
from exeptions import (
    InvalidTokenError,
    InvalidAnswerError,
    InvalidLevelError,
    GameNotStartedError,
    ForbiddenError
)

class DatabaseManager:
    @staticmethod
    def getGameState(session: Session):
        query = select(GameState).where(GameState.id == 1)
        gameState = session.exec(query).first()
        if not gameState:
            gameState = GameState()
            session.add(gameState)
            session.commit()

        return gameState

    @staticmethod
    def checkToken(session: Session, token: str):
        query = select(exists().where(Team.uuid == token))
        result = session.exec(query).one()
        if not result:
            raise InvalidTokenError

    @staticmethod
    def checkStatus(session: Session):
        state = DatabaseManager.getGameState(session)
        if GameStatus(state.status) != GameStatus.Started:
            raise GameNotStartedError

    @staticmethod
    def checkExerciseAccess(session: Session, level: int, token: str):
        DatabaseManager.checkStatus(session)
        DatabaseManager.checkToken(session, token)
        team = DatabaseManager.getTeamByToken(session, token)

        if level > team.currentLevel:
            raise ForbiddenError
        
        return team
    
    @staticmethod
    def checkResultsAccess(session: Session, token: str):
        team = DatabaseManager.getTeamByToken(session, token)
        if team.currentLevel <= team.getLastLevel():
            raise ForbiddenError
        
        return team

    @staticmethod
    def getTeamByToken(session: Session, token: str):
        team = session.get(Team, token)
        if not team:
            raise InvalidTokenError
        
        return team
    
    @staticmethod
    def getExerciseByLevel(session: Session, level: int):
        exercise = session.get(Exercise, level)
        if not exercise:
            raise InvalidLevelError
        
        return exercise
    
    @staticmethod
    def checkAnswer(session: Session, team: Team, answer: Answer):
        if team.currentLevel >= answer.level:
            solution = session.get(Exercise, answer.level)
        else:
            raise ForbiddenError

        if solution:
            return answer.answer == solution.solution
        else:
            raise InvalidAnswerError
    
    @staticmethod
    def getTeams(session: Session):
        statement = select(Team)
        teams = session.exec(statement).all()
        return teams
    
    @staticmethod
    def getExercises(session: Session):
        statement = select(Exercise)
        exercises = session.exec(statement).all()
        return exercises
    
    @staticmethod
    def getTeamNameAvailability(session, teamName: str):
        statement = select(exists().where(Team.name == teamName))
        isNameTaken = bool(session.exec(statement).one())
        return isNameTaken
    
    def __init__(self, databasePath: Path):
        self.databasePath = databasePath
        self.databasePath.parent.mkdir(parents = True, exist_ok = True)
        self.databaseEngine = create_engine(f"sqlite:///{self.databasePath.as_posix()}", echo = True)
        SQLModel.metadata.create_all(self.databaseEngine)

    def getSession(self):
        return Session(self.databaseEngine)