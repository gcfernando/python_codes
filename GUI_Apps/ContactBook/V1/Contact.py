import pyodbc
import ttkbootstrap as ttk
from ttkbootstrap.dialogs import Messagebox
from contextlib import contextmanager


class ContactBook:
    # Connection string for the SQL database
    __sql_connection = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=GEHAN-FERNANDO;DATABASE=Test;UID=sa;PWD=1qaz2wsx@'

    def __init__(self):
        # Initialize the main window with ttkbootstrap
        self.master = ttk.Window(themename='sandstone')
        self.master.title('Contact book')

        # Define initial dimensions for the window
        self.__id = 0
        self.__width = 490
        self.__height = 160

        # Set the geometry and minimum and maximum size of the window
        self.master.geometry(f'{self.__width}x{self.__height}')
        self.master.minsize(width=self.__width, height=self.__height)
        self.master.maxsize(width=self.__width, height=self.__height)

        # Center the window on the screen and create UI widgets
        self.center_window()
        self.create_widgets()

        # Start the tkinter main loop
        self.master.mainloop()

    def center_window(self):
        # Centers the window on the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        x_coordinate = int((screen_width / 2) - (self.__width / 2))
        y_coordinate = int((screen_height / 2) - (self.__height / 2))
        self.master.geometry(
            f'{self.__width}x{self.__height}+{x_coordinate}+{y_coordinate}')

    def create_widgets(self):
        # Create and layout all widgets in the main window
        label_header = ttk.Label(
            self.master, text='Personal details', bootstyle="primary")
        label_header.grid(row=0, column=0, columnspan=2)

        # Create entry fields for personal details
        self.fNameEntry, self.fNameVar = self.create_entry('First Name', 1, 40)
        self.lNameEntry, self.lNameVar = self.create_entry('Last Name', 2, 40)
        self.mNumberEntry, self.mNumberVar = self.create_entry(
            'Mobile #', 3, 50)
        self.mAddressEntry, self.mAddressVar = self.create_entry(
            'Email', 4, 50)

        # Create a frame for control buttons
        frame_Control = ttk.Frame(self.master)
        frame_Control.grid(row=1, column=2, rowspan=4,
                           sticky='n', padx=10, pady=5)

        # Create control buttons (Save, Delete, Search, Reset)
        self.save_button = self.create_button(
            frame_Control, 'Save', 'primary', self.save_information, 1)
        self.delete_button = self.create_button(
            frame_Control, 'Delete', 'danger', self.delete_information, 1)
        self.search_button = self.create_button(
            frame_Control, 'Search', 'info', self.search_information, 1)
        self.reset_button = self.create_button(
            frame_Control, 'Reset', 'secondary', self.reset_information, 1)

        # Set focus to the first name entry field and disable the delete button initially
        self.fNameEntry.focus_set()
        self.delete_button['state'] = 'disabled'

    def create_entry(self, label_text, row, width):
        # Helper function to create a labeled entry field
        label = ttk.Label(self.master, text=label_text)
        label.grid(row=row, column=0, sticky='w', padx=5)

        frame = ttk.Frame(self.master)
        frame.grid(row=row, column=1, padx=1, pady=1, sticky='w')

        entry_var = ttk.StringVar()
        entry = ttk.Entry(frame, width=width, textvariable=entry_var)
        entry.pack(side='left')

        return (entry, entry_var)

    def create_button(self, master, text, style, command, pady):
        # Helper function to create a button
        button = ttk.Button(master, text=text, style=style,
                            width=10, command=command)
        button.pack(pady=pady)

        return button

    def execute_sql(self, sql_command, params=None, fetch_result=False):
        # # Execute an SQL command with optional parameters
        with self.database_connection() as connection:
            cursor = connection.cursor()
            cursor.execute(sql_command, params)

            if fetch_result:
                result = cursor.fetchone()
            else:
                result = None

            connection.commit()
            return result

    @contextmanager
    def database_connection(self):
        # Context manager for establishing a database connection
        connection = pyodbc.connect(ContactBook.__sql_connection)
        try:
            yield connection
        finally:
            connection.close()

    def save_information(self):
        # Save contact information to the database
        params = {
            'id': self.__id,
            'fname': self.fNameVar.get().strip(),
            'lname': self.lNameVar.get().strip(),
            'mnumber': self.mNumberVar.get().strip(),
            'maddress': self.mAddressVar.get().strip()}

        if self.validate_params(params):
            Messagebox.show_warning(
                message='None of the information can be empty.', title='Contact Book')
            return

        try:
            # Call the stored procedure to save the contact
            sql_command = "EXEC SaveContact @id=?, @fname=?, @lname=?, @mnumber=?, @maddress=?"
            self.execute_sql(sql_command, [
                             params['id'], params['fname'], params['lname'], params['mnumber'], params['maddress']])
            Messagebox.show_info(message='Information saved successfully.',
                                 title='Contact Book')
            self.reset_information()
        except pyodbc.Error as e:
            print(str(e))
            Messagebox.show_error(
                message='An error occurred while saving information.', title='Contact Book')

    def delete_information(self):
        # Delete contact information from the database
        try:
            sql_command = "EXEC DeleteContact @id=?"
            self.execute_sql(sql_command, [self.__id])
            Messagebox.show_info(message='Information deleted successfully.',
                                 title='Contact Book')
            self.reset_information()
        except pyodbc.Error as e:
            print(str(e))
            Messagebox.show_error(
                message='An error occurred while deleting information.', title='Contact Book')

    def search_information(self):
        # Search for contact information in the database
        params = {
            'mnumber': self.mNumberVar.get().strip(),
            'maddress': self.mAddressVar.get().strip()}

        try:
            # Call the stored procedure to search for the contact
            sql_command = "EXEC SearchContact @mnumber=?, @maddress=?"
            contact = self.execute_sql(
                sql_command, [params['mnumber'], params['maddress']], fetch_result=True)

            if contact is None:
                Messagebox.show_warning(
                    message='Information was not found for the given query.', title='Contact Book')
            else:
                # Update UI with the found contact information
                self.__id = contact[0]
                self.fNameVar.set(contact[1])
                self.lNameVar.set(contact[2])
                self.mNumberVar.set(contact[3])
                self.mAddressVar.set(contact[4])

                self.fNameEntry.focus_set()
                self.delete_button['state'] = 'enabled'
        except pyodbc.Error as e:
            print(str(e))
            Messagebox.show_error(
                message='An error occurred while searching information.', title='Contact Book')

    def reset_information(self):
        # Reset the entry fields to their default state
        self.fNameVar.set('')
        self.lNameVar.set('')
        self.mNumberVar.set('')
        self.mAddressVar.set('')
        
        self.__id = 0
        self.fNameEntry.focus_set()
        self.delete_button['state'] = 'disabled'

    def validate_params(self, params):
        # Validate the parameters to ensure they are not empty
        return any(v == '' for v in params.values())


# Run the ContactBook application
if __name__ == "__main__":
    ContactBook()
