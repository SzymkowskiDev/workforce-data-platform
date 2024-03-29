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
from wdp.custom_loggers import config
from typing import Union

level_to_log: int = logging.DEBUG

dir_path = os.path.dirname(os.path.abspath(__file__))
data_folder = os.path.join(dir_path, config.SUB_FOLDER, config.GENERAL_LOG_PATH)
LOG_PATH = data_folder

parameters: dict[str, Union[int, str, list[logging.Handler]]] = {
    'level': level_to_log,
    'handlers': [
        logging.FileHandler(LOG_PATH),
        logging.StreamHandler()
    ]
}


class GenericLogger:
    def __init__(self) -> None:
        """
        Initializes the GenericLogger class with string FUNC_LOG_FORMAT and configures logging with the parameters
        """
        self.logger_format: str = config.FUNC_LOG_FORMAT
        logging.basicConfig(**parameters, format=self.logger_format)
        self.logger: logging.Logger = logging.getLogger(__name__)

    @staticmethod
    def get_logger(name: str = None, use_decorator_format: bool = False) -> logging.Logger:
        logger = logging.getLogger(name)
        logger_format = config.DECORATOR_LOG_FORMAT if use_decorator_format else config.FUNC_LOG_FORMAT
        formatter = logging.Formatter(logger_format)
        for handler in logger.handlers:
            handler.setFormatter(formatter)
        logger.setLevel(level_to_log)
        return logger


def get_default_logger(use_decorator_format: bool = True) -> logging.Logger:
    return GenericLogger().get_logger(use_decorator_format=use_decorator_format)


def log(
    function=None, *,
    new_logger: Union[GenericLogger, logging.Logger] = None,
    level: int = logging.DEBUG,
    message="No message"
):
    """
        :param function: callable = None
        :param new_logger: Union[GenericLogger, logging.Logger] = None
            The new logger instance to use, by default None.
        :param level: int, optional
        :param message: str, optional
        :return: logging.Logger
            A logger instance
        This is a decorator function that logs messages for a given function.
        It takes any function to decorate, a logger object, a log level, and a message as arguments
        """

    def decorator_log(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            frame = inspect.currentframe().f_back
            filename = inspect.getframeinfo(frame).filename
            module_name = filename.split('/')[-1].split('.')[0]
            line_number = inspect.getframeinfo(frame).lineno
            lineno = inspect.getsourcelines(func)[1]

            logger: logging.Logger = get_default_logger(use_decorator_format=False)
            try:
                if not new_logger:
                    first_arg = args[0] if args else None
                    logger_params = [x for x in (*args, *kwargs.values()) if isinstance(x, (logging.Logger, GenericLogger))]
                    if hasattr(first_arg, "__dict__"):
                        logger_params += [x for x in first_arg.__dict__.values() if isinstance(x, (logging.Logger, GenericLogger))]
                    logger_container = logger_params[0] if logger_params else GenericLogger()
                else:
                    logger_container = new_logger

                if isinstance(logger_container, GenericLogger):
                    logger = logger_container.get_logger(func.__name__, use_decorator_format=False)
                else:
                    logger = logger_container

                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                arguments = ", ".join(args_repr + kwargs_repr)

                if not arguments:
                    arguments = "No args"

                get_default_logger(use_decorator_format=True)
                logger.log(level, f" Message: {message}, Class: {func.__qualname__}, Function: {func.__name__}, called with args:"
                                  f" {arguments}, from module {module_name}, called from line {line_number}, executed at line {lineno}")
                get_default_logger(use_decorator_format=False)
            except Exception as err:
                logger.info(f"Exception raised in {func.__name__} during args shuffling. Exception: {str(err)}")
                pass  # as it's just a logger, I don't want it to cause any interruptions before logging

            try:
                # in case decorated function raise any exception log it, and then reraise
                result = func(*args, **kwargs)
                return result
            except Exception as err:
                logger.exception(f"Exception raised in {func.__name__}. Exception: {str(err)}. Details:")
                raise err
        return wrapper

    if not function:
        return decorator_log
    else:
        return decorator_log(function)
