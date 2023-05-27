# Developer ::> Gehan Fernando

"""
Do we need to apply Serializable ?

It depends on how you intend to use the CustomException class. If you plan to use this exception class only within a single process or application,
then there may be no need to make it serializable. 

However, if you intend to use this exception class in a distributed environment, 
where exceptions can be raised in one process or machine and caught in another, then you may need to make it serializable.

"""

class CustomException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

def some_function():
    x = 5
    y = 6
    # do something
    if x < y:
        raise CustomException("Something went wrong")
    # do something else

try:
    some_function()
except CustomException as e:
    print(e.message)