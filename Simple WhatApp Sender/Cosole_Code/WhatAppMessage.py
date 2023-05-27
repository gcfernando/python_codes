# Developer ::> Gehan Fernando
# Reference : https://pypi.org/project/pywhatkit/
# import libraries
import pywhatkit as pw

# Before you run the application, open WhatApp in a web browser.

# Set the phone number of the recipient (include the country code, without any + or 0)
phone_number = "+46*********"

# Set the message you want to send
message = "Hi there, message to WhatApp using pywhatkit."

# Set the time at which you want to send the message (24-hour format)
hour = 21
min = 5

# Call the sendwhatmsg() function from pywhatkit, passing in the phone number, message, and send time
pw.sendwhatmsg(phone_no= phone_number, message= message, time_hour= hour, time_min= min, tab_close= True)