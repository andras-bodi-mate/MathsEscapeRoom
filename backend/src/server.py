import sqlite3
from enum import Enum
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, create_engine, select, exists

from core import Core
from team import Team, Difficulty

class AnswerResponse(Enum):
    Wrong = 0
    Correct = 1
    Finished = 2

class Answer(BaseModel):
    level: int
    answer: int

class ProblemQuery(BaseModel):
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

class Server:
    solutions = {
        1: 4172,
        2: 6202,
        3: 3745,
        4: 9513,
        5: 1144,
        6: 5865,
        7: 4242,
        8: 7942
    }

    adminPanelUsername = "foldes-pi-nap-admin"
    adminPanelPassword = "pi-nap-31415"

    @staticmethod
    def checkToken(session: Session, token: str):
        query = select(exists().where(Team.uuid == token))
        result = session.exec(query).one()
        if not result:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Invalid token")

    @staticmethod
    def getTeamFromToken(session: Session, token: str):
        team = session.get(Team, token)
        if not team:
            raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Invalid token")
        
        return team
    
    @staticmethod
    def checkAnswer(team: Team, answer: Answer):
        return team.currentLevel >= answer.level and answer.level in Server.solutions and Server.solutions[answer.level] == answer.answer
    
    @staticmethod
    def getTeams(session: Session):
        statement = select(Team)
        teams = session.exec(statement).all()
        return teams

    def __init__(self):
        self.app = FastAPI()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins = [
                "http://localhost:3500",
                "http://127.0.0.1:3500",
                "http://212.48.252.191:3500"
            ],
            allow_credentials = True,
            allow_methods = ["*"],
            allow_headers = ["*"],
        )

        self.databasePath = Core.getPath("backend/data/database.db")
        self.databasePath.parent.mkdir(parents = True, exist_ok = True)
        self.databaseEngine = create_engine(f"sqlite:///{self.databasePath.as_posix()}", echo = True)
        #SQLModel.metadata.drop_all(self.databaseEngine)
        SQLModel.metadata.create_all(self.databaseEngine)
 
        self.security = HTTPBasic()

        def authenticate(self, credentials: HTTPBasicCredentials = Depends(self.security)):
            if credentials.username != Server.adminPanelUsername or credentials.password != Server.adminPanelPassword:
                raise HTTPException(
                    status_code = status.HTTP_401_UNAUTHORIZED,
                    detail = "Incorrect username or password",
                    headers = {"WWW-Authenticate": "Basic"},
                )

        @self.app.get("/info")
        async def getTeamInfo(token: str = Header(alias = "Authorization")):
            with Session(self.databaseEngine) as session:
                Server.checkToken(session, token)
                query = select(Team).where(Team.uuid == token)
                team = session.exec(query).one()
            
            return {"teamName": team.name, "difficulty": team.getDifficulty(), "currentLevel": team.currentLevel}

        @self.app.get("/results")
        async def getTeamResults():
            with Session(self.databaseEngine) as session:
                teams = Server.getTeams(session)

                numFinishedTeams = 0
                for team in teams:
                    finishLevel = 6 if team.getDifficulty() == Difficulty.Easy else 8
                    if team.currentLevel - 1 == finishLevel:
                        numFinishedTeams += 1

            return {"numTeams": len(teams), "numFinishedTeams": numFinishedTeams}

        @self.app.post("/available")
        async def checkAvailability(query: TeamNameAvailabilityQuery):
            with Session(self.databaseEngine) as session:
                statement = select(exists().where(Team.name == query.teamName))
                isNameTaken = session.exec(statement).one()

            if isNameTaken:
                return {"available": False}
            else:
                return {"available": True}

        @self.app.post("/register")
        async def register(teamInfo: TeamRegistrationInfo):
            with Session(self.databaseEngine) as session:
                team = Team(name = teamInfo.teamName, difficulty = teamInfo.difficulty.value)
                session.add(team)
                session.commit()

                teamUuid = team.uuid

            return {"token": teamUuid}

        @self.app.post("/check")
        async def checkAnswer(answer: Answer, token: str = Header(alias = "Authorization")):
            with Session(self.databaseEngine) as session:
                Server.checkToken(session, token)
                team = Server.getTeamFromToken(session, token)

                if answer.level > team.currentLevel:
                    raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "The team hasn't reached that level yet")

                if Server.checkAnswer(team, answer):
                    team.currentLevel = answer.level + 1
                    if answer.level == team.getLastLevel():
                        response = {"result": AnswerResponse.Finished}
                    else:
                        response = {"result": AnswerResponse.Correct}
                else:
                    response = {"result": AnswerResponse.Wrong}

                session.add(team)
                session.commit()

            return JSONResponse(jsonable_encoder(response))
        
        @self.app.post("/problem")
        async def getProblem(problemQuery: ProblemQuery, token: str = Header(alias = "Authorization")):
            with Session(self.databaseEngine) as session:
                Server.checkToken(session, token)
                team = Server.getTeamFromToken(session, token)

                if problemQuery.level > team.currentLevel:
                    raise HTTPException(status_code = status.HTTP_403_FORBIDDEN)

                problemPaths = list(Core.getPath(f"backend/res/problems").glob(f"{problemQuery.level}.*"))

            if len(problemPaths) > 0 and problemPaths[0].exists():
                return FileResponse(problemPaths[0])
            else:
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Couldn't find problem")
            
        @self.app.post("/delete")
        async def deleteTeam(teamDeletionRequest: TeamDeletionInfo):
            with Session(self.databaseEngine) as session:
                team = Server.getTeamFromToken(session, teamDeletionRequest.teamUuid)
                session.delete(team)
                session.commit()

        @self.app.post("/modify")
        async def modifyTeam(teamModificationRequest: TeamModificationInfo):
            with Session(self.databaseEngine) as session:
                team = Server.getTeamFromToken(session, teamModificationRequest.teamUuid)
                team.name = teamModificationRequest.newTeamName
                team.difficulty = teamModificationRequest.newDifficulty.value
                team.currentLevel = teamModificationRequest.newLevel
                session.add(team)
                session.commit()
        
        @self.app.get("/teams")
        async def getTeams():
            with Session(self.databaseEngine) as session:
                teams = Server.getTeams(session)

            return [
                {
                    "uuid": team.uuid,
                    "name": team.name,
                    "difficulty": team.getDifficulty(),
                    "currentLevel": team.currentLevel,
                    "lastLevel": team.getLastLevel()
                }
            for team in teams]
        
        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc):
            print(f"The client sent invalid data!: {exc}")
            return await request_validation_exception_handler(request, exc)