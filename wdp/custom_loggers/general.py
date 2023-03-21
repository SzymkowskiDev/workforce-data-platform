"""
Logger created by tomekkurzydlak for easy logging in Python, using just the @log decorator.

Usage:
    from wdp.custom_loggers import log, GenericLogger

    Use the @log decorator to log details with default logger. You can specify the logging level and message as below:

    @log(level=logging.INFO, message='Function called: ')
    def my_function(arg1, arg2):
        pass

    Both parameters are optional. By default, provided level is DEBUG, and you can use the @log decorator as easy as:

    @log
    def my_function(arg1, arg2):
        pass

    You can also pass your own logger to @log decorator:

    new_logger = logging.getLogger("new logger")
    @log(my_logger=new_logger)

    This will use your object and will not create any new logger.

    You can also use GenericLogger class directly to create a logger object:

    logger_from_generic_class = GenericLogger().get_logger(name="from GenericLogger class")
    def calculate_sum(a, b):
        logger_from_generic_class.debug("logger from GenericLogger class")
        return a + b

    Logs are saved to "general_logs.txt" file and printed to console
    The logs include time, level, the function name, class name (if in class method), and arguments passed to the function.

    You can configure path, log format and custom messages in config.py file
"""

import logging
import functools
import inspect
import os
import wdp.custom_loggers.config as config
from typing import Union

level_to_log: int = logging.DEBUG
log_format: str = config.GENERAL_LOG_FORMAT
log_format_s: str = config.GENERAL_LOG_FORMAT_S

FILE_PATH: str = config.GENERAL_LOG_PATH
SUB_FOLDER: str = config.SUB_FOLDER
dir_path = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(dir_path, SUB_FOLDER, FILE_PATH)
LOG_PATH = data_folder

messages = config.CUSTOM_MESSAGES

parameters: dict[str, Union[int, str, list[logging.Handler]]] = {
    'level': level_to_log,
    'handlers': [
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
}


class GenericLogger:
    def __init__(self) -> None:
        self.logger_format: str = log_format_s
        logging.basicConfig(**parameters, format=self.logger_format)
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def get_logger(name: str = None, use_decorator_format: bool = False) -> logging.Logger:
        logger = logging.getLogger(name)
        if use_decorator_format:
            logger_format = log_format
        else:
            logger_format = log_format_s
        formatter = logging.Formatter(logger_format)
        for handler in logger.handlers:
            handler.setFormatter(formatter)
        logger.setLevel(level_to_log)
        return logger


def get_default_logger(use_decorator_format: bool = True) -> logging.Logger:
    return GenericLogger().get_logger(use_decorator_format=use_decorator_format)


def log(
    func_to_decorate=None, *,
    my_logger: Union[GenericLogger, logging.Logger] = None,
    level: int = logging.DEBUG,
    message=None
):
    if not message:
        message = messages.get(level, "No message available")

    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            frame = inspect.currentframe().f_back
            filename = inspect.getframeinfo(frame).filename
            module_name = filename.split('/')[-1].split('.')[0]
            line_number = inspect.getframeinfo(frame).lineno
            lineno = inspect.getsourcelines(func)[1]

            # check if passed logger is an instance of GenericLogger class or logging.Logger and set the string format
            # if my_logger is None:
            #     use_decorator_format = True
            # else:
            #     use_decorator_format = not isinstance(my_logger, (logging.Logger, GenericLogger))
            logger: logging.Logger = get_default_logger(use_decorator_format=False)
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
                    logger = logger_container.get_logger(func.__name__, use_decorator_format=False)
                else:
                    logger = logger_container

                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                arguments = ", ".join(args_repr + kwargs_repr)

                if not arguments:
                    arguments = "No args provided"
                # if multiple objects was passed the format parameter may be still set incorrectly,
                # so set it to True manually. This will not create any new logger object
                get_default_logger(use_decorator_format=True)
                logger.log(level, f" Message: {message}, Class: {func.__qualname__}, Function: {func.__name__}, called with args:"
                                  f" {arguments}, from module {module_name}, called from line {line_number}, executed at {lineno}")
                get_default_logger(use_decorator_format=False)
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
