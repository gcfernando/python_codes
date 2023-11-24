# Developer Gehan Fernando
# import libraries
import qrcode

# Defines the data (URL) to be encoded in the QR code.
data = 'View my profile : www.linkedin.com/in/gehan-fernando'

# Creating an instance of QRCode class
qr = qrcode.QRCode(version=1,
                   box_size=15,
                   border=5)  # Creates a new instance of the QRCode class with specified version, box size, and border.

# Adds the defined data to the 'qr' instance.
qr.add_data(data)

# Generates the QR code, allowing it to fit the data appropriately.
qr.make(fit=True)

# Creates an image of the QR code with specified colors for the QR code and its background.
img = qr.make_image(fill_color='darkblue',
                    back_color='lightgray')

# Saves the generated QR code image to a file named 'profile.png'.
img.save('profile.png')
