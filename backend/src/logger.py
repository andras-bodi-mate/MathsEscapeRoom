import sty
from inspect import stack
import pathlib


class Logger:
    @staticmethod
    def log(message):
        callerStackFrame = stack()[2]
        callerFile = callerStackFrame.filename
        callerFileName = f"[{pathlib.Path(callerFile).name}]"
        print(f"{callerFileName:<20} {message}")

    @staticmethod
    def getMessageFromValues(values):
        return ' '.join(map(str, values))

    @staticmethod
    def logDebug(*values):
        Logger.log(sty.fg.grey + Logger.getMessageFromValues(values) + sty.rs.all)

    @staticmethod
    def logInfo(*values):
        Logger.log(sty.fg.li_cyan + Logger.getMessageFromValues(values) + sty.rs.all)

    @staticmethod
    def logWarning(*values):
        Logger.log(sty.fg.yellow + Logger.getMessageFromValues(values) + sty.rs.all)

    @staticmethod
    def logError(*values):
        Logger.log(sty.fg.red + sty.ef.bold + Logger.getMessageFromValues(values) + sty.rs.all)

    @staticmethod
    def logCriticalError(*values):
        Logger.log(sty.fg.magenta + sty.ef.bold + Logger.getMessageFromValues(values) + sty.rs.all)
