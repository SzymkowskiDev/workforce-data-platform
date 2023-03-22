# ----------- LOGS FOLDER -----------

SUB_FOLDER = "log"

# ----------- GENERAL LOG -----------

DECORATOR_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
FUNC_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - Message: %(message)s - Function: %(funcName)s," \
                       " from module %(module)s, line %(lineno)s"
GENERAL_LOG_PATH = "general_logs.txt"

CUSTOM_MESSAGES = {
    10: "This is a debug message",
    20: "This is an info message",
    30: "This is a warning message",
    40: "This is an error message",
    50: "This is a critical message"
}

# ----------- PROFILER LOG -----------

PROFILING_ENABLED = True  # enables profiling

CONSOLE_PROFILER = True  # enables printing to console
TXT_PROFILER = True  # enables saving to readable txt file
JSON_PROFILER = True  # enables saving to JSON
PLOT_PROFILER = True  # enables png plot

SORT_METHOD = "cumulative"

PROFILER_TXT_PROFILER_PATH: str = "profiler_logs.txt"
PROFILER_JSON_PROFILER_PATH: str = "profiler_logs.json"
PROFILER_PLOT_PROFILER_PATH: str = "profiler_plot.png"