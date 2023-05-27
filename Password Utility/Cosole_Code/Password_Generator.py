# Developer ::> Gehan Fernando
# import libraries
import random
import string

def generate_password(length, num_digits, num_uppercase, num_lowercase, num_special_chars):
    digits = string.digits
    uppercase_letters = string.ascii_uppercase
    lowercase_letters = string.ascii_lowercase
    special_chars = string.punctuation

    num_chars = num_digits + num_uppercase + num_lowercase + num_special_chars
    if num_chars > length:
        raise ValueError("The total number of requested characters exceeds the length of the password.")

    password = ""

    # Add the required number of digits
    password += ''.join(random.choice(digits) for i in range(num_digits))
    # Add the required number of uppercase letters
    password += ''.join(random.choice(uppercase_letters) for i in range(num_uppercase))
    # Add the required number of lowercase letters
    password += ''.join(random.choice(lowercase_letters) for i in range(num_lowercase))
    # Add the required number of special characters
    password += ''.join(random.choice(special_chars) for i in range(num_special_chars))
    # Add random characters until the password reaches the desired length
    while len(password) < length:
        password += random.choice(digits + uppercase_letters + lowercase_letters + special_chars)

    # Shuffle the password string to ensure randomness
    password_list = list(password)
    random.shuffle(password_list)
    password = "".join(password_list)

    return password

if __name__ == "__main__":
    password = generate_password(length=30, num_digits=5, num_uppercase=5, num_lowercase=5, num_special_chars=5)
    print(password)