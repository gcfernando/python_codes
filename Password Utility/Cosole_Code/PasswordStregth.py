# Developer ::> Gehan Fernando
# import libraries
import os, re

def password_strength(password):
    special_characters = r'[!@#$%^&*()_+={}\[\]|\\:;"\'<>,.?/`~]'
    lower = len(re.findall(r'[a-z]', password))
    upper = len(re.findall(r'[A-Z]', password))
    digits = len(re.findall(r'\d', password))
    special = len(re.findall(special_characters, password))
    
    # calculate the number of possibilities for each type of character
    lower_possibilities = 26 ** lower
    upper_possibilities = 26 ** upper
    digit_possibilities = 10 ** digits
    special_possibilities = len(special_characters) ** special
    
    # calculate the total number of possibilities
    total_possibilities = lower_possibilities * upper_possibilities * digit_possibilities * special_possibilities
    
    # determine the strength of the password based on the total number of possibilities
    THRESHOLDS = {10 ** 16: "Very Strong", 10 ** 12: "Strong", 10 ** 8: "Moderate", 10 ** 4: "Weak"}

    return next((strength for threshold, strength in THRESHOLDS.items() if total_possibilities >= threshold), "Very Weak")

if __name__ == "__main__":
   os.system('cls')

   while True:
    password = input("Enter your password: ")
    password_status = password_strength(password)
    print(password_status,end="\r\n")
    
    status = input("More ! (Y|N) : ")

    if status == "Y" or  status == "y":
        os.system('cls')
    else:
        break