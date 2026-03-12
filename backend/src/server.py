from enum import Enum
from fastapi import FastAPI, HTTPException, Request, Response, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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

    @staticmethod
    def checkToken(token: str):
        if token not in Team.uuidTeamMap:
            raise HTTPException(status_code = 404, detail = "Invalid token")

    @staticmethod
    def checkAnswer(team: Team, answer: Answer):
        return team.currentLevel >= answer.level and answer.level in Server.solutions and Server.solutions[answer.level] == answer.answer

    def __init__(self):
        self.app = FastAPI()

        self.app.add_middleware(
            CORSMiddleware,
            allow_origins = [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "*"
            ],
            allow_credentials = True,
            allow_methods = ["*"],
            allow_headers = ["*"],
        )

        self.teams: list[Team] = []

        @self.app.get("/info")
        async def getTeamInfo(token: str = Header(alias = "Authorization")):
            Server.checkToken(token)
            team = Team.uuidTeamMap[token]
            return {"teamName": team.name, "difficulty": team.difficulty, "currentLevel": team.currentLevel}

        @self.app.get("/results")
        async def getTeamResults():
            numFinishedTeams = 0
            for team in self.teams:
                finishLevel = 6 if team.difficulty == Difficulty.Easy else 8
                if team.currentLevel - 1 == finishLevel:
                    numFinishedTeams += 1
            return {"numTeams": len(self.teams), "numFinishedTeams": numFinishedTeams}

        @self.app.post("/available")
        async def checkAvailability(query: TeamNameAvailabilityQuery):
            for team in self.teams:
                if team.name == query.teamName:
                    return {"available": False}
            return {"available": True}

        @self.app.post("/register")
        async def register(teamInfo: TeamRegistrationInfo):
            team = Team(teamInfo.teamName, teamInfo.difficulty)
            self.teams.append(team)
            return {"token": team.uuid}

        @self.app.post("/check")
        async def checkAnswer(answer: Answer, token: str = Header(alias = "Authorization")):
            Server.checkToken(token)
            team = Team.uuidTeamMap[token]

            if Server.checkAnswer(team, answer):
                team.currentLevel = answer.level + 1
                if answer.level == team.lastLevel:
                    response = {"result": AnswerResponse.Finished}
                else:
                    response = {"result": AnswerResponse.Correct}
            else:
                response = {"result": AnswerResponse.Wrong}
            return JSONResponse(jsonable_encoder(response))
        
        @self.app.post("/problem")
        async def getProblem(problemQuery: ProblemQuery, token: str = Header(alias = "Authorization")):
            Server.checkToken(token)
            team = Team.uuidTeamMap[token]

            if problemQuery.level > team.currentLevel:
                raise HTTPException(status_code = 403)

            problemPaths = list(Core.getPath(f"backend/res/problems").glob(f"{problemQuery.level}.*"))

            if len(problemPaths) > 0 and problemPaths[0].exists():
                return FileResponse(problemPaths[0])
            else:
                raise HTTPException(status_code = 404, detail = "Couldn't find problem")