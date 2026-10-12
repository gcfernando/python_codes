# Call a C# DLL from Python with pythonnet — Load a .NET Library

Demonstrates **how to call a compiled C# / .NET library (DLL) from Python** using `pythonnet` and its `clr` module.

## Overview

This project shows cross-language interoperability between Python and .NET. A simple `Calculator` class is compiled as a C# class library (DLL), and Python loads it at runtime via the `clr` (Common Language Runtime) module from the `pythonnet` package. The Python script then calls the .NET methods directly as if they were native Python functions.

## Features

- Load and call a .NET assembly (`.dll`) from Python
- Calls five static methods on the C# `Calc` class — a description plus four arithmetic operations:
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

You also need a **.NET runtime** that can load the DLL. `Calculator.csproj` targets **.NET 6** (`net6.0`).

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

The script calls `Addition(5, 5)`, `Subtraction(10, 5)`, `Multiplication(5, 5)`, and `Division(10, 5)`, so it prints:

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
- `Calc` is a `public static class`, so its methods are called directly on the type (`Calc.Addition(5, 5)`) without creating an instance.

## Troubleshooting

- **The DLL fails to load on Windows.** By default `pythonnet` 3 uses the .NET Framework runtime on Windows, while this DLL targets .NET 6. Select the .NET (Core) runtime before importing `clr`:

  ```python
  from pythonnet import load
  load("coreclr")
  import clr
  ```

  The machine needs a .NET runtime that can run a `net6.0` assembly, or rebuild the library for the runtime you have installed.
- **`FileNotFoundException` for the DLL** — the path passed to `clr.AddReference` must point to the DLL on your machine.

## Related Projects

- [The reverse direction: call Python from C# with Python.NET](https://github.com/gcfernando/csharp_codes/tree/main/PythonBridge)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
