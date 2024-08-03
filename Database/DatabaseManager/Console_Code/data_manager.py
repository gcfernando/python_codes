# Developer ::> Gehan Fernando
# import libraries
import dbm

# Define user data
user_data = {
    'first_name': 'Gehan',
    'last_name': 'Fernando',
    'age': '43',
    'country': 'Sri Lanka'
}

# Function to save user data to the database
def save_user_data(filename, data):
    with dbm.open(filename, 'c') as db:
        for key, value in data.items():
            db[key] = value

# Function to load user data from the database
def load_user_data(filename):
    with dbm.open(filename, 'r') as db:
        return {key: db[key].decode() for key in db.keys()}

# Save user data
save_user_data('user.db', user_data)

# Load and display user data
user_info = load_user_data('user.db')
content = (f'Hi, I am {user_info["first_name"]} {user_info["last_name"]}. '
           f'I live in {user_info["country"]}, and I am {user_info["age"]} years old.')

print(content)