"""
Profiler created by tomekkurzydlak for easy profiling in Python, using just the @profile decorator.

Usage:
    from wdp.custom_loggers import profile

    Then use the @profile decorator to profile your code as below:

    @profile
    def my_function(arg1, arg2):
        pass

    When using with other decorators, like @log, make sure to place the @profile decorator at the bottom
    to prevent the function profiling with other functions:

    @log
    @profile
    def my_function(arg1, arg2):
        pass

    Profiler saves data by default to json file and prints it to the console, but it also can dump readable
    logs to text file and plot the most important values exporting it to png file.

    You can customise behaviour and change log path in a config.py file
"""
import cProfile
import pstats
import json
import psutil
import os
import functools
import datetime
import matplotlib.pyplot as plt
from typing import Any, Callable
import wdp.custom_loggers.config as config

profiling_enabled: bool = config.PROFILING_ENABLED

console_profiler: bool = config.CONSOLE_PROFILER
txt_profiler: bool = config.TXT_PROFILER
json_profiler: bool = config.JSON_PROFILER
plot_profiler: bool = config.PLOT_PROFILER

TXT_PROFILER_PATH: str = config.PROFILER_TXT_PROFILER_PATH
JSON_PROFILER_PATH: str = config.PROFILER_JSON_PROFILER_PATH
PLOT_PROFILER_PATH: str = config.PROFILER_PLOT_PROFILER_PATH
SUB_FOLDER: str = config.SUB_FOLDER
sort_method: str = config.SORT_METHOD

dir_path = os.path.dirname(os.path.abspath(__file__))
plot_profiler_path = os.path.join(dir_path, SUB_FOLDER, PLOT_PROFILER_PATH)
json_profiler_path = os.path.join(dir_path, SUB_FOLDER, JSON_PROFILER_PATH)
txt_profiler_path = os.path.join(dir_path, SUB_FOLDER, TXT_PROFILER_PATH)

now = datetime.datetime.now()
now_str: str = now.strftime("%d/%m/%Y %H:%M:%S")
timestamp: float = now.timestamp()


def print_to_console(func: callable, memory: float, stats: pstats.Stats) -> None:
    """ Prints profiler statistics and memory usage to console """
    print("=" * 10, f"Stats for function: {func.__name__}", "=" * 10)
    stats.strip_dirs()
    stats.sort_stats(sort_method).print_stats()
    print(f"Memory usage: {memory:.2f} MB\n")
    print("=" * 10, f"Generated {now_str}", "=" * 10)


def log_to_json(func: callable, memory: float, stats: pstats.Stats) -> None:
    """ Logs profiler statistics and memory usage to a JSON file """
    string = {
        "captured_data": {
            "timestamp": timestamp,
            "log_time": now_str,
            'function_name': func.__name__,
            'memory_usage': round(memory, 2),
            'time_usage': round(stats.total_tt, 5),
            'calls': stats.total_calls,
        }
    }
    try:
        with open(json_profiler_path, mode="r") as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = []
    except FileNotFoundError:
        data = []
    finally:
        data.append(string)
        with open(json_profiler_path, mode="w") as file:
            json.dump(data, file, indent=4)


def log_to_txt(profiler: cProfile.Profile, memory: float, func: callable) -> None:
    """ Logs profiler statistics and memory usage to a text file """
    with open(txt_profiler_path, 'a') as file:
        stats = pstats.Stats(profiler, stream=file)
        stats.stream = file
        file.write("\n" + "=" * 30 + f" Stats for function: {func.__name__} " + "=" * 30 + "\n")
        stats.sort_stats(sort_method).print_stats()
        file.write(f"Memory usage: {memory:.2f} MB\n")
        file.write("=" * 30 + f" Generated {now_str} " + "=" * 30 + "\n")


def plot() -> None:
    """ Creates a plot based on the profiling results """
    if not os.path.exists(json_profiler_path):
        print("Cannot plot. Profiler data file does not exist")
        return

    with open(json_profiler_path, "r") as f:
        try:
            data = json.load(f)
            if not all(key in data[0]["captured_data"] for key in ["function_name", "memory_usage", "time_usage", "calls"]):
                print("Cannot plot. Profiler data file does not contain valid keys")
                return
        except (json.JSONDecodeError, IndexError):
            print("Cannot plot. Profiler data file is empty or corrupted")
            return

    memory_data = [(entry["captured_data"]["function_name"], entry["captured_data"]["memory_usage"]) for entry in data]
    time_data = [(entry["captured_data"]["function_name"], entry["captured_data"]["time_usage"]) for entry in data]
    calls_data = [(entry["captured_data"]["function_name"], entry["captured_data"]["calls"]) for entry in data]

    fig, axs = plt.subplots(3, figsize=(10, 10))

    axs[0].plot([entry[0] for entry in memory_data], [entry[1] for entry in memory_data], 'o-')
    axs[0].set_title("Memory Usage")
    axs[0].set_xlabel("Time")
    axs[0].set_ylabel("Memory Usage (MB)")

    axs[1].plot([entry[0] for entry in time_data], [entry[1] for entry in time_data], 'o-')
    axs[1].set_title("Time Usage")
    axs[1].set_xlabel("Time")
    axs[1].set_ylabel("Time (s)")

    axs[2].plot([entry[0] for entry in calls_data], [entry[1] for entry in calls_data], 'o-')
    axs[2].set_title("Number of Function Calls")
    axs[2].set_xlabel("Time")
    axs[2].set_ylabel("Number of Calls")

    plt.tight_layout()
    plt.savefig(plot_profiler_path)


def profile(func) -> Callable:
    """Decorator that profiles the execution of a function

    Args:
        func: Function to be profiled

    Returns:
        Wrapped function that has been profiled
    """
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if profiling_enabled:
            profiler = cProfile.Profile()
            result = profiler.runcall(func, *args, **kwargs)
            stats = pstats.Stats(profiler)
            memory_usage = psutil.Process(os.getpid()).memory_info().rss / 1024 / 1024
            if console_profiler:
                print_to_console(func, memory_usage, stats)
            if txt_profiler:
                log_to_txt(profiler, memory_usage, func)
            if json_profiler:
                log_to_json(func, memory_usage, stats)
            if plot_profiler:
                plot()
        else:
            return func(*args, **kwargs)
        return result
    return wrapper
