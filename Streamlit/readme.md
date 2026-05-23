# Streamlit Demo

A comprehensive Streamlit web application demonstrating a wide range of widgets, layout features, and data visualizations.

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
