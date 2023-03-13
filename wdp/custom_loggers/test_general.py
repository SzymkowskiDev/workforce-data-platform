# import logging
# from general import *
from wdp.custom_loggers.general import *

# from wdp import log
# from general import *


# loger = MyLogger()
# debugger = Debugger("general_logs.log")


# try:
#     # Call function to get employee salary
# salary = get_employee_salary(1234)

# except Exception as e:
#     handle_exception(general_logger)

@log
def for_loop(f):
    b = []
    for n in range(f):
        b.append(n)
    return b


@log(level=logging.CRITICAL, message="Comprehension")
def comprehension():
    b = [n for n in range(1000000)]
    return b


@log(level=logging.INFO, message="nothing to report")
class TestClass:
    def __init__(self, name, creator):
        self.name = name
        self.creator = creator

    @log
    def say_hello(self):
        print(f"This is a test object called {self.name}, constructed by {self.creator}")


for_loop(1000000)
comprehension()
test = TestClass("Test #3", "Tomek")
test.say_hello()
