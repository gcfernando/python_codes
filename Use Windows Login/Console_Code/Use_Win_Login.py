# Developer ::> Gehan Fernando
# import libraries
import getpass, win32security

def authenticate_user():
    # Retrieve the username of the currently logged-in user
    username = getpass.getuser() 
    # Prompt the user to enter their Windows password securely
    password = getpass.getpass("Enter your Windows password: ")

    try:
        win32security.LogonUser(
            username,
            None,
            password,
            win32security.LOGON32_LOGON_NETWORK,  # Logon type for network access
            win32security.LOGON32_PROVIDER_DEFAULT  # Default logon provider
        )
        print("Login successful!")
        # Proceed with your application logic here
    except win32security.error as e:
        print("Login failed. Exiting application.")
        # Perform any necessary cleanup or error handling

# Call the authentication function
authenticate_user()