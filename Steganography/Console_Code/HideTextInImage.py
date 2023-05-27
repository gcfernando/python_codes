# Developer ::> Gehan Fernando
# Import libraries
from stegano import lsb

# Define the text that we want to hide in the image
hidden_text = """
Life is a journey full of ups and downs, twists and turns. At times, we may feel lost or discouraged, 
wondering if we're on the right path. However, it's important to remember that each obstacle is an opportunity for growth and learning. 
Don't give up on your dreams, no matter how difficult the road may seem. Keep pushing forward, believing in yourself and your abilities. 
Surround yourself with positive influences and never underestimate the power of hard work and perseverance. 
Remember, success is not measured by the number of times we fall but by how many times we get back up. 
Embrace the journey, stay determined, and you will achieve greatness.
"""

# Define the file paths for the original image and the output image
original_image = 'C:\Gehan\Projects\Python\Cat.png'
output_image = 'C:\Gehan\Projects\Python\CatSecrect.png'

# Use the lsb.hide() method to hide the text in the image
secret = lsb.hide(original_image, hidden_text.strip())

# Save the resulting image with the hidden text as the output image
secret.save(output_image)

# Use the lsb.reveal() method to extract the hidden text from the output image
read_from_image = lsb.reveal(output_image)

# Print the extracted text to the console, with any leading or trailing whitespace removed
print(read_from_image.strip())