# Developer ::> Gehan Fernando
# import libraries
import clr

# Load the C# assembly
clr.AddReference(r'C:\Gehan\Projects\Python\LoadLibraries\Library\Calculator.dll')

# Import the namespaces and classes from the Calculator DLL
from Calculator import Calc

# Use the C# library in Python
about = Calc.About()
addition = Calc.Addition(5, 5)
subtraction = Calc.Subtraction(10, 5)
multiplication = Calc.Multiplication(5, 5)
division = Calc.Division(10, 5)

# Print the results
print(f'About: {about}\n')
print(f'Addition: {addition}')
print(f'Subtraction: {subtraction}')
print(f'Multiplication: {multiplication}')
print(f'Division: {division}')