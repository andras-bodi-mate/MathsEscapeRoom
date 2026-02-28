from fastapi import FastAPI, HTTPException, Request, Response, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from core import Core

class Answer(BaseModel):
    level: int
    answer: int

class Server:
    solutions = {
        1: 1000,
        2: 2200,
        3: 3330,
        4: 4444
    }

    tipPaths = {
        1: Core.getPath("backend/res/tips/1.png")
    }

    @staticmethod
    def checkAnswer(answer: Answer):
        return answer.level in Server.solutions and Server.solutions[answer.level] == answer.answer

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

        @self.app.post("/check/")
        async def checkAnswer(answer: Answer):
            if Server.checkAnswer(answer):
                response = {"correct": True}
            else:
                response = {"correct": False}
            return JSONResponse(jsonable_encoder(response))
        
        @self.app.post("/tip/")
        async def getTip(answer: Answer):
            if Server.checkAnswer(answer) and answer.level in Server.tipPaths:
                return FileResponse(Server.tipPaths[answer.level])
            else:
                raise HTTPException(status_code = 404, detail = "Couldn't find tip")