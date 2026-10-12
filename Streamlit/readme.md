# Streamlit Example App in Python — Widgets, DataFrames and Charts

A single-file **Streamlit example app** in Python that demonstrates sidebar input widgets, a pandas DataFrame, a matplotlib histogram, and Streamlit's native line and area charts — a quick way to learn how to build an interactive data web app without writing HTML or JavaScript.

## Overview

This app serves as a showcase of Streamlit's core capabilities. Users can interact with various sidebar controls, view their selections displayed in the main area, explore a dynamically generated data table, and see multiple chart types — all in a single-page web interface.

## Features

- **Sidebar widgets:**
  - Slider (age range selection)
  - Text input (name)
  - Selectbox (gender)
  - Multiselect (hobbies)
  - Date input (date of birth)
  - Number input (salary)
  - Checkbox (terms agreement)
  - Radio buttons (feedback source)

- **Main area:**
  - Display of all user inputs
  - Dynamic DataFrame combining user input with sample data
  - Age distribution histogram (matplotlib)
  - Salary-vs-age line chart (Streamlit native)
  - Salary-vs-age area chart (Streamlit native)
  - Conditional "Show More Info" section via checkbox

## Requirements

```
streamlit
pandas
numpy
matplotlib
```

Install dependencies:

```bash
pip install streamlit pandas numpy matplotlib
```

## Usage

From the `Console_Code` folder:

```bash
streamlit run streamlit_app.py
```

If the above command does not work:

```bash
python -m streamlit run streamlit_app.py
```

The app opens automatically in your default browser at `http://localhost:8501`.

## File Structure

```
Streamlit/
└── Console_Code/
    └── streamlit_app.py    # Main Streamlit application
```

## How Streamlit Runs the App

Streamlit re-runs the whole script from top to bottom every time a widget changes. Each widget call (for example `st.sidebar.slider`) returns its current value, so the page always reflects the latest inputs without callbacks.

## Related Projects

- [Local AI chat app with Ollama and Streamlit](https://github.com/gcfernando/document/blob/main/local_ai_learning_lab.md)
- [WiFi Radar — Flask web dashboard](../Wifi%20Radar/readme.md)
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
