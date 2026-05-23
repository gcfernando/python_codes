# Load Libraries

Demonstrates how to call a compiled .NET (C#) library from Python using `pythonnet`.

## Overview

This project shows cross-language interoperability between Python and .NET. A simple `Calculator` class is compiled as a C# class library (DLL), and Python loads it at runtime via the `clr` (Common Language Runtime) module from the `pythonnet` package. The Python script then calls the .NET methods directly as if they were native Python functions.

## Features

- Load and call a .NET assembly (`.dll`) from Python
- Demonstrates four arithmetic operations via the C# `Calc` class:
  - `About()` — returns a description string
  - `Addition(a, b)`
  - `Subtraction(a, b)`
  - `Multiplication(a, b)`
  - `Division(a, b)`

## Project Structure

```
LoadLibraries/
├── Calculator/
│   ├── Calc.cs               # C# source — static Calculator class
│   ├── Calculator.csproj     # .NET project file
│   └── Calculator.sln        # .NET solution file
├── Console_Code/
│   └── CalcCaller.py         # Python script that loads and calls the DLL
└── Library/
    └── Calculator.dll        # Compiled .NET class library
```

## Requirements

```
pythonnet
```

Install the dependency:

```bash
pip install pythonnet
```

You also need the **.NET runtime** installed on your system (compatible with the compiled DLL version).

## Usage

The DLL is pre-compiled and located in `Library/Calculator.dll`. Update the path in `CalcCaller.py` if needed:

```python
clr.AddReference(r'path\to\Library\Calculator.dll')
```

Then run the script:

```bash
python Console_Code/CalcCaller.py
```

### Example Output

```
About: You're accessing .NET library

Addition: 10.0
Subtraction: 5.0
Multiplication: 25.0
Division: 2.0
```

## Rebuilding the DLL

If you need to recompile the C# library:

```bash
cd Calculator
dotnet build --configuration Release
```

Copy the resulting `.dll` from the `bin/Release/` output to `Library/Calculator.dll`.

## Notes

- The DLL path in `CalcCaller.py` is currently hardcoded. Update it to match your actual directory structure before running.
- `asyncio`, `pprint`, and `copy` are part of the Python standard library and do not need installation.
