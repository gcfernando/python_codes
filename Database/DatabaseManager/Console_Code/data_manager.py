# Developer ::> Gehan Fernando
# import libraries
import dbm

# Open the database and write data
with dbm.open('user.db', 'c') as db:
    db['first_name'] = 'Gehan'
    db['last_name'] = 'Fernando'
    db['age'] = '43'  # Note: dbm stores values as bytes, so convert to bytes
    db['country'] = 'Sri Lanka'

# Open the database and read data
with dbm.open('user.db', 'r') as db:
    firstName = db.get(b'first_name').decode()  # Decode bytes to string
    lastName = db.get(b'last_name').decode()  # Decode bytes to string
    age = db.get(b'age').decode()  # Decode bytes to string
    country = db.get(b'country').decode()  # Decode bytes to string

    content = f'Hi, I am {firstName} {lastName}. I live in {country}, and I am {age} years old.'

    print(content)