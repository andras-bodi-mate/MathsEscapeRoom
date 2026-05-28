from pathlib import Path

import uvicorn

from src.logger import Logger
from src.server import Server
from src.core import Core

def main():
    Logger.logInfo("Program started")
    server = Server()
    uvicorn.run(server.app, host = "0.0.0.0", port = 3501)

if __name__ == "__main__":
    main()
