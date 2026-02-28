from pathlib import Path

import uvicorn

from logger import Logger
from server import Server
from core import Core

def main():
    Logger.logInfo("Program started")
    server = Server()
    uvicorn.run(server.app, host = "0.0.0.0", port = 8000)

if __name__ == "__main__":
    main()
