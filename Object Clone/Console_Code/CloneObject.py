# Developer ::> Gehan Fernando
# Import libraries
import copy

"""
If you want to create a true copy of an object, you can use the deepcopy method. 
The deepcopy method creates a new object with a new reference and recursively clones all the attributes of the original object.
"""

# define a class
class MyClass:
    def __init__(self, x):
        self.x = x

# create an instance of MyClass
original_object = MyClass(10)

# clone the object using deepcopy method
cloned_object = copy.deepcopy(original_object)

# modify the original object
original_object.x = 20

# print the attributes of both objects
print(original_object.x)  # 20
print(cloned_object.x)    # 10