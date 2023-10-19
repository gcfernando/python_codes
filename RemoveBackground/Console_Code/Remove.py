# Developer ::> Gehan Fernando
# import necessary libraries
from rembg import remove
from PIL import Image
import io

def remove_background(input_path, output_path):
    """
    Remove the background from the image specified by input_path and 
    save the resultant image to output_path with a white background.

    Args:
    - input_path (str): Path to the input image.
    - output_path (str): Path to save the output image with background removed.
    """

    # Open the input image using a context manager to ensure it's properly closed after use
    with Image.open(input_path) as img_input:
        
        # Convert the image to PNG format bytes (rembg generally expects PNG input)
        image_bytes = io.BytesIO()
        img_input.save(image_bytes, format="PNG")

        # Use rembg's remove function to get the image data without background
        out_img = remove(image_bytes.getvalue())
        
        # Open the resultant image data using PIL's Image module
        with Image.open(io.BytesIO(out_img)) as result_img:

            # Create a white / black canvas of the same size as the result image
            white_canvas = Image.new('RGB', result_img.size, 'black')
            
            # Paste the result image onto the white canvas
            # This will replace the transparent background with white
            white_canvas.paste(result_img, (0, 0), result_img)

            # Save to the specified output path
            white_canvas.save(output_path)

if __name__ == "__main__":
    # Define the input and output image paths
    orginal_image = 'Elephant.jpg'
    output_image = 'Elephant_Modified.jpg'

    # Call the remove_background function to process the image
    remove_background(orginal_image, output_image)
