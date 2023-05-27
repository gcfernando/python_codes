# Developer ::> Gehan Fernando
# import libraries
import pywhatkit

# Set the path of the input image file
image_path = 'C:\Gehan\Projects\Python\Car.jpeg'

# Set the path of the output text file
text_path = 'C:\Gehan\Projects\Python\Car.txt'

# Calling the image_to_ascii_art() method of pywhatkit module to convert the 
# input image to ASCII art and save it in the output text file
pywhatkit.image_to_ascii_art(img_path= image_path, output_file= text_path)