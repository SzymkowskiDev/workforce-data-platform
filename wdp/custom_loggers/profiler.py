import cProfile
import pstats
import json
import psutil
import os
import functools
import datetime
import matplotlib.pyplot as plt

console_profiler = True
txt_profiler = True
json_profiler = True
plot_profiler = True

TXT_PROFILER_PATH: str = "profiler_logs.txt"
JSON_PROFILER_PATH: str = "profiler_logs.json"
PLOT_PROFILER_PATH: str = "profiler_plot.png"
sort_method = "cumulative"

now = datetime.datetime.now()
now_str = now.strftime("%d/%m/%Y %H:%M:%S")
timestamp = now.timestamp()


def print_to_console(func, memory, stats):
    print("=" * 10, f"Stats for function: {func.__name__}", "=" * 10)
    stats.sort_stats(sort_method).print_stats()
    print(f"Memory usage: {memory:.2f} MB\n")
    print("=" * 10, f"Generated {now_str}", "=" * 10)


def log_to_json(func, memory, stats):
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
        with open(JSON_PROFILER_PATH, mode="r") as file:
            try:
                data = json.load(file)
            except json.decoder.JSONDecodeError:
                data = []
    except FileNotFoundError:
        data = []
    finally:
        data.append(string)
        with open(JSON_PROFILER_PATH, mode="w") as file:
            json.dump(data, file, indent=4)


def log_to_txt(profiler, memory, func):
    with open(TXT_PROFILER_PATH, 'a') as file:
        stats = pstats.Stats(profiler, stream=file)
        stats.stream = file
        file.write("\n" + "=" * 30 + f" Stats for function: {func.__name__} " + "=" * 30 + "\n")
        stats.sort_stats(sort_method).print_stats()
        file.write(f"Memory usage: {memory:.2f} MB\n")
        file.write("=" * 30 + f" Generated {now_str} " + "=" * 30 + "\n")


def plot():
    with open(JSON_PROFILER_PATH, "r") as f:
        data = json.load(f)

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
    plt.savefig(PLOT_PROFILER_PATH)


def profile(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
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

        return result
    return wrapper


