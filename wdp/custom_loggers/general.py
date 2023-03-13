"""
Module created by JimmyHodl for easy logging in Python, using just the @log decorator.

Usage:
    from wdp.custom_loggers.general import *

    Then use the @log decorator to log details. You can specify the logging level and message as below:

    @log(level=logging.INFO, message='Function called: ')
    def my_function(arg1, arg2):
        pass

    Both parameters are optional. By default, provided level is DEBUG, and you can use the @log decorator as easy as:
    @log
    def my_function(arg1, arg2):
        pass

    Logs are saved to "general_logs.txt" file and printed to console with the DEBUG level.
    The logs include the function name, class name (if in class method), and arguments passed to the function.

    You can find and change log path, log format and logging level parameters right below import statements.
"""

import logging
import functools
from typing import Union

level_to_log: int = logging.DEBUG
log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_PATH: str = "general_logs.txt"

parameters: dict[str, Union[int, str, list[logging.Handler]]] = {
    'level': level_to_log,
    'format': log_format,
    'handlers': [
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
}


class GenericLogger:
    def __init__(self) -> None:
        """
        Initializes the GenericLogger class and configures logging with the parameters
        """
        logging.basicConfig(**parameters)
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def get_logger(name: str = None) -> logging.Logger:
        return logging.getLogger(name)


def get_default_logger() -> logging.Logger:
    return GenericLogger().get_logger()


def log(
    func_to_decorate=None, *,
    my_logger: Union[GenericLogger, logging.Logger] = None,
    level: int = logging.DEBUG,
    message: str = "No message provided"
):
    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger: logging.Logger = get_default_logger()
            try:
                if not my_logger:
                    first_args = next(iter(args), None)
                    logger_params = [
                        x for x in kwargs.values()
                        if isinstance(x, logging.Logger) or isinstance(x, GenericLogger)
                    ] + [
                        x for x in args
                        if isinstance(x, logging.Logger) or isinstance(x, GenericLogger)
                    ]
                    if hasattr(first_args, "__dict__"):
                        logger_params = logger_params + [
                            x for x in first_args.__dict__.values()
                            if isinstance(x, logging.Logger)
                            or isinstance(x, GenericLogger)
                        ]
                    logger_container = next(iter(logger_params), GenericLogger())
                else:
                    logger_container = my_logger

                if isinstance(logger_container, GenericLogger):
                    logger = logger_container.get_logger(func.__name__)
                else:
                    logger = logger_container

                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                arguments = ", ".join(args_repr + kwargs_repr)
                if not arguments:
                    arguments = "No args provided"
                logger.log(level, f" Message: {message}, Class: {func.__qualname__}, Function: {func.__name__}, called with args:"
                                  f" {arguments}")
            except Exception:
                pass

            try:
                result = func(*args, **kwargs)
                return result
            except Exception as err:
                logger.exception(f"Exception raised in {func.__name__}. Exception: {str(err)}. Details:")
                raise err
        return wrapper

    if not func_to_decorate:
        return decorator_log
    else:
        return decorator_log(func_to_decorate)
