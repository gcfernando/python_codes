# Developer ::> Gehan Fernando
# import libraries
import os, sys
import io
import pyglet
import PySimpleGUI as sg
from PIL import Image

# Set the theme for the GUI
sg.theme("DarkTeal10")

# Function to determine the resource path
def resource_path(relative_path):
    """ Get the absolute path to the resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Define folders for fonts, images, and data
font_folder = resource_path('Fonts')
image_folder = resource_path('Images')
data_folder = resource_path('Data')

# Initialize the current index and the list to store image information
current_index = 0
image_information = []


def button_control(index):
    # Determine the states of 'previous' and 'next' buttons
    is_first = index <= 0
    is_last = index >= len(image_information) - 1

    # Update the 'previous' button state
    window['previous'].update(disabled=is_first)

    # Update the 'next' button state
    window['next'].update(disabled=is_last)


def read_file(file_path):
    """Read the contents of a file and return them."""
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except IOError as e:
        print(f"Error reading file {file_path}: {e}")
        return None


def read_information():
    """Read image and corresponding data files, storing their paths and content."""
    global image_information
    image_information = []
    for image_name in os.listdir(image_folder):
        if image_name.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(image_folder, image_name)
            data_path = os.path.join(
                data_folder, os.path.splitext(image_name)[0] + '.txt')
            if os.path.exists(data_path):
                data_content = read_file(data_path)
                formatted_data_content = data_content.replace('. ', '.\n')
                if data_content:
                    image_information.append(
                        (image_path, formatted_data_content.strip()))


def load_image(index):
    """Load and display the image and its data based on the current index."""
    if 0 <= index < len(image_information):
        image_path, data_content = image_information[index]

        # Open and resize the image
        with Image.open(image_path) as img:
            # Resizes the image in-place
            img.thumbnail((300, 300), Image.Resampling.LANCZOS)

            # Convert to byte array for PySimpleGUI
            with io.BytesIO() as output:
                img.save(output, format="PNG")
                data = output.getvalue()

        window['fruitImage'].update(data=data)
        window['fruitImage'].set_tooltip(data_content)


# Load custom fonts
pyglet.font.add_file(os.path.join(font_folder, 'Futura.ttf'))

# Define font styles
title_font = ('Futura', 30, 'bold')
button_font = ('Futura', 12, 'bold')

# Layout for the title and controls (buttons and image display)
layout = [
    [sg.Text('Welcome to Fruit WiKi', size=(20, 1),
             font=title_font, text_color='lime green', justification='center', expand_x=True)],
    [sg.Button('Previous', enable_events=True, key='previous', disabled=True,
               size=(10, 2), font=button_font),
     sg.Image(size=(300, 300), key='fruitImage'),
     sg.Button('Next', enable_events=True, key='next',
               size=(10, 2), font=button_font)]
]

# Create the window
window = sg.Window('Fruit Wiki', layout, finalize=True)

# Read image and data information
read_information()
load_image(current_index)

# Event loop for the GUI
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Exit'):
        break
    elif event == 'previous':
        current_index -= 1
        button_control(current_index)
        load_image(current_index)
    elif event == 'next':
        current_index += 1
        button_control(current_index)
        load_image(current_index)

# Close the window when the loop is exited
window.close()
