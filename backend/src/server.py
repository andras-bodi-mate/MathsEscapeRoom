from fastapi import FastAPI, Request, Response, Header
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
            if answer.level in Server.solutions and Server.solutions[answer.level] == answer.answer:
                response = {"correct": True}
            else:
                response = {"correct": False}
            return JSONResponse(jsonable_encoder(response))