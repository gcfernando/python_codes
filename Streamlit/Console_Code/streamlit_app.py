# Developer ::> Gehan Fernando
# import libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Title and Description
st.title("Beautiful Streamlit App Example")
st.markdown("""
This is a comprehensive example of a Streamlit app. It covers various widgets, layout management, data visualization, and data frames.
""")

# Sidebar with Widgets
st.sidebar.header("User Input")
st.sidebar.markdown("Use the controls below to filter data.")

# Slider
age = st.sidebar.slider("Select Age Range", 18, 70, (25, 40))

# Text Input
name = st.sidebar.text_input("Enter your name", "Gehan Fernando")

# Selectbox
gender = st.sidebar.selectbox("Select Gender", ["Male", "Female", "Other"])

# Multiselect
hobbies = st.sidebar.multiselect("Select Hobbies", ["Reading", "Traveling", "Cooking", "Gaming", "Sports"])

# Date Input
date_of_birth = st.sidebar.date_input("Select Date of Birth", pd.to_datetime("1990-01-01"))

# Number Input
salary = st.sidebar.number_input("Enter Salary", min_value=30000, max_value=200000, value=50000, step=5000)

# Checkbox
agree = st.sidebar.checkbox("I agree to the terms and conditions")

# Radio buttons
feedback = st.sidebar.radio("How did you hear about us?", ["Social Media", "Friend", "Advertisement", "Other"])

# Displaying User Inputs
st.header("User Inputs")
st.write(f"**Name:** {name}")
st.write(f"**Age Range:** {age[0]} - {age[1]}")
st.write(f"**Gender:** {gender}")
st.write(f"**Hobbies:** {', '.join(hobbies) if hobbies else 'None'}")
st.write(f"**Date of Birth:** {date_of_birth}")
st.write(f"**Salary:** ${salary}")
st.write(f"**Feedback Source:** {feedback}")
st.write(f"**Agreement:** {'Agreed' if agree else 'Not Agreed'}")

# Creating a DataFrame
data = pd.DataFrame({
    'Name': [name, "Alice", "Bob", "Charlie"],
    'Age': [np.random.randint(20, 70), 30, 25, 40],
    'Gender': [gender, "Female", "Male", "Male"],
    'Salary': [salary, 60000, 50000, 80000],
    'Hobbies': [', '.join(hobbies), "Reading", "Gaming", "Sports"]
})

# Displaying DataFrame
st.header("User Data")
st.write("Here is the data based on your inputs:")
st.dataframe(data)

# Data Visualization
st.header("Data Visualization")

# Bar Chart
st.subheader("Age Distribution")
fig, ax = plt.subplots()
ax.hist(data['Age'], bins=10, color='skyblue', edgecolor='black')
ax.set_title('Age Distribution')
ax.set_xlabel('Age')
ax.set_ylabel('Frequency')
st.pyplot(fig)

# Line Chart
st.subheader("Salary Over Age")
st.line_chart(data[['Age', 'Salary']].set_index('Age'))

# Area Chart
st.subheader("Salary Area Chart")
st.area_chart(data[['Age', 'Salary']].set_index('Age'))

# Checkbox for hiding/showing additional content
if st.checkbox("Show More Info"):
    st.subheader("Additional Information")
    st.write("You can add more interactive elements here, like forms, more charts, or even APIs!")

# Footer
st.markdown("""
---
**This is a simple demonstration of the features of Streamlit.** Feel free to modify and extend this example.
""")