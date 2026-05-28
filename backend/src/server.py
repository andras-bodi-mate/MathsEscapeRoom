from fastapi import FastAPI, HTTPException, status, Header, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import request_validation_exception_handler
from fastapi.exceptions import RequestValidationError

from core import Core
from models import (
    Team
)
from enums import (
    Difficulty,
    GameStatus,
    AnswerResponse
)
from exeptions import (
    InvalidAnswerError,
    GameNotStartedError,
    ForbiddenError
)
from schemas import (
    Answer,
    TeamNameAvailabilityQuery,
    TeamRegistrationInfo,
    AccessQuery,
    AccessQueryPath,
    ExerciseQuery,
    TeamDeletionInfo,
    TeamModificationInfo,
    ExerciseDeletionInfo,
    ExerciseModificationInfo,
    GameControlInfo
)
from databaseManager import DatabaseManager

class Server:
    # solutions = {
    #     1: 4172,
    #     2: 6202,
    #     3: 3745,
    #     4: 9513,
    #     5: 1144,
    #     6: 5865,
    #     7: 4242,
    #     8: 7942
    # }

    adminPanelUsername = "foldes-pi-nap-admin"
    adminPanelPassword = "pi-nap-31415"

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

        self.databaseManager = DatabaseManager(Core.getPath("backend/data/database.db"))

        @self.app.get("/info")
        async def getTeamInfo(token: str = Header(alias = "Authorization")):
            with self.databaseManager.getSession() as session:
                team = self.databaseManager.getTeamByToken(session, token)
            
            return {"teamName": team.name, "difficulty": team.getDifficulty(), "currentLevel": team.currentLevel}

        @self.app.get("/results")
        async def getTeamResults():
            with self.databaseManager.getSession() as session:
                teams = self.databaseManager.getTeams(session)

            numFinishedTeams = 0
            for team in teams:
                finishLevel = 6 if team.getDifficulty() == Difficulty.Easy else 8
                if team.currentLevel - 1 == finishLevel:
                    numFinishedTeams += 1

            return {"numTeams": len(teams), "numFinishedTeams": numFinishedTeams}

        @self.app.post("/available")
        async def checkAvailability(query: TeamNameAvailabilityQuery):
            with self.databaseManager.getSession() as session:
                isNameTaken = self.databaseManager.getTeamNameAvailability(session, query.teamName)

            if isNameTaken:
                return {"available": False}
            else:
                return {"available": True}

        @self.app.post("/register")
        async def register(teamInfo: TeamRegistrationInfo):
            with self.databaseManager.getSession() as session:
                try:
                    self.databaseManager.checkStatus(session)
                except GameNotStartedError:
                    raise HTTPException(status.HTTP_403_FORBIDDEN)
                team = Team(name = teamInfo.teamName, difficulty = teamInfo.difficulty.value)
                session.add(team)
                session.commit()

                teamUuid = team.uuid

            return {"token": teamUuid}
        
        @self.app.post("/access")
        async def canAccess(accessQuery: AccessQuery, token: str = Header(alias = "Authorization")):
            with self.databaseManager.getSession() as session:
                match accessQuery.path:
                    case AccessQueryPath.Exercise if accessQuery.level:
                        try:
                            self.databaseManager.checkExerciseAccess(session, accessQuery.level, token)
                            hasAccess = True
                        except (ForbiddenError, GameNotStartedError):
                            hasAccess = False

                    case AccessQueryPath.Results:
                        try:
                            self.databaseManager.checkResultsAccess(session, token)
                            hasAccess = True
                        except ForbiddenError:
                            hasAccess = False

                    case _:
                        raise HTTPException(status.HTTP_400_BAD_REQUEST, "The specified path does not exist")
                    
            return {"hasAccess": hasAccess}

        @self.app.post("/check")
        async def checkAnswer(answer: Answer, token: str = Header(alias = "Authorization")):
            with self.databaseManager.getSession() as session:
                self.databaseManager.checkStatus(session)
                self.databaseManager.checkToken(session, token)
                team = self.databaseManager.getTeamByToken(session, token)

                if answer.level > team.currentLevel:
                    raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = "The team hasn't reached that level yet")

                try:
                    isAnswerCorrect = self.databaseManager.checkAnswer(session, team, answer)
                except ForbiddenError:
                    raise HTTPException(status.HTTP_403_FORBIDDEN)
                except InvalidAnswerError:
                    raise HTTPException(status.HTTP_400_BAD_REQUEST)

                if isAnswerCorrect:
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
        
        @self.app.post("/exercise")
        async def getExercise(exerciseQuery: ExerciseQuery, token: str = Header(alias = "Authorization")):
            with self.databaseManager.getSession() as session:
                self.databaseManager.checkExerciseAccess(session, exerciseQuery.level, token)

                exercisePaths = list(Core.getPath(f"backend/res/exercises").glob(f"{exerciseQuery.level}.*"))

            if len(exercisePaths) > 0 and exercisePaths[0].exists():
                return FileResponse(exercisePaths[0])
            else:
                raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Couldn't find exercise")
            
        @self.app.post("/title")
        async def getExerciseTitle(exerciseQuery: ExerciseQuery, token: str = Header(alias = "Authorization")):
            with self.databaseManager.getSession() as session:
                self.databaseManager.checkExerciseAccess(session, exerciseQuery.level, token)
                exercise = self.databaseManager.getExerciseByLevel(session, exerciseQuery.level)
                
            return {
                "title": exercise.title
            }
            
        @self.app.post("/teams/delete")
        async def deleteTeam(teamDeletionRequest: TeamDeletionInfo):
            with self.databaseManager.getSession() as session:
                team = self.databaseManager.getTeamByToken(session, teamDeletionRequest.teamUuid)
                session.delete(team)
                session.commit()

        @self.app.post("/teams/modify")
        async def modifyTeam(teamModificationRequest: TeamModificationInfo):
            with self.databaseManager.getSession() as session:
                team = self.databaseManager.getTeamByToken(session, teamModificationRequest.teamUuid)
                team.name = teamModificationRequest.newTeamName
                team.difficulty = teamModificationRequest.newDifficulty.value
                team.currentLevel = teamModificationRequest.newLevel
                session.add(team)
                session.commit()

        @self.app.post("/exercises/delete")
        async def deleteTeam(exerciseDeletionRequest: ExerciseDeletionInfo):
            with self.databaseManager.getSession() as session:
                exercise = self.databaseManager.getExerciseByLevel(session, exerciseDeletionRequest.level)
                session.delete(exercise)
                session.commit()

        @self.app.post("/exercises/modify")
        async def modifyTeam(exerciseModificationRequest: ExerciseModificationInfo):
            with self.databaseManager.getSession() as session:
                exercise = self.databaseManager.getExerciseByLevel(session, exerciseModificationRequest.level)
                exercise.level = exerciseModificationRequest.newLevel
                exercise.title = exerciseModificationRequest.newTitle
                exercise.solution = exerciseModificationRequest.newSolution
                session.add(exercise)
                session.commit()

        @self.app.post("/control")
        async def controlGame(gameControlInfo: GameControlInfo):
            with self.databaseManager.getSession() as session:
                currentState = self.databaseManager.getGameState(session)
                currentState.status = gameControlInfo.newStatus.value
                session.add(currentState)
                session.commit()
        
        @self.app.get("/teams")
        async def getTeams():
            with self.databaseManager.getSession() as session:
                teams = self.databaseManager.getTeams(session)

            return [
                {
                    "uuid": team.uuid,
                    "name": team.name,
                    "difficulty": team.getDifficulty(),
                    "currentLevel": team.currentLevel,
                    "lastLevel": team.getLastLevel()
                }
            for team in teams]

        @self.app.get("/exercises")
        async def getExercises():
            with self.databaseManager.getSession() as session:
                exercises = self.databaseManager.getExercises(session)

            return [
                {
                    "level": exercise.level,
                    "title": exercise.title,
                    "solution": exercise.solution
                }
                
            for exercise in exercises]
        
        @self.app.get("/state")
        async def getStatus():
            with self.databaseManager.getSession() as session:
                gameState = self.databaseManager.getGameState(session)
                gameState = {"status": GameStatus(gameState.status)}

            return gameState

        @self.app.exception_handler(RequestValidationError)
        async def validationExceptionHandler(request, exc):
            print(f"The client sent invalid data:")
            print(exc)
            return await request_validation_exception_handler(request, exc)
