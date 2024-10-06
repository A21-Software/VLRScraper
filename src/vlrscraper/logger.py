import os
import sys
import logging

from typing import Optional


class LogConfig:
    formatter: Optional[logging.Formatter] = None
    stdoutHandler: logging.StreamHandler = logging.StreamHandler(sys.stdout)
    fileHandler: Optional[logging.FileHandler] = None
    setup: bool = False
    logger: logging.Logger


def get_logger() -> logging.Logger:
    return LogConfig.logger


def set_should_print(shouldprint: bool) -> None:
    if shouldprint:
        get_logger().addHandler(LogConfig.stdoutHandler)
    else:
        get_logger().removeHandler(LogConfig.stdoutHandler)


def set_format(format: str) -> None:
    LogConfig.formatter = logging.Formatter(format)
    LogConfig.stdoutHandler.setFormatter(LogConfig.formatter)
    if LogConfig.fileHandler:
        LogConfig.fileHandler.setFormatter(LogConfig.formatter)


def setup_logging(stdout: bool, directory: str = "logs", level: int = logging.DEBUG):
    if not LogConfig.setup:
        LogConfig.logger = logging.getLogger(__name__)
        if not os.path.isdir(directory):
            os.mkdir(directory)
        LogConfig.fileHandler = logging.FileHandler(
            os.path.join(directory, "log.log"), "w"
        )
        LogConfig.fileHandler.setLevel(logging.DEBUG)
        LogConfig.logger.addHandler(LogConfig.fileHandler)
        set_format("%(created)f:%(levelname)s:%(name)s:%(module)s:%(message)s")
        set_should_print(stdout)
        LogConfig.setup = True


def teardown_logging():
    LogConfig.formatter = None
    LogConfig.fileHandler = None
    LogConfig.setup = False
