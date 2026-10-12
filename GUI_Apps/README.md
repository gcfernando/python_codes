# Python Desktop GUI Apps — Tkinter (ttkbootstrap) Contact Book with SQL Server

A collection of desktop GUI applications built with Python. It currently contains **Contact Book**, a CRUD contact manager that shows how to connect a **Tkinter / ttkbootstrap** interface to **Microsoft SQL Server** using **pyodbc** and stored procedures.

---

## Applications

### Contact Book

A desktop contact management application with a graphical interface backed by a Microsoft SQL Server database. It is a practical example of a Python GUI that saves, searches, updates, and deletes records in SQL Server through parameterized stored-procedure calls.

**Location:** `ContactBook/V1/Contact.py`

#### Features

- Add new contacts with first name, last name, mobile number, and email address
- Search contacts by mobile number or email address
- Update existing contact details
- Delete contacts from the database
- Input validation to prevent empty submissions
- Duplicate detection enforced at the database level (unique mobile number and email)
- Centered, fixed-size window with a clean `sandstone` theme

#### Screenshots / UI

The application presents a simple form with four input fields and four action buttons:

| Field | Description |
|---|---|
| First Name | Contact's first name |
| Last Name | Contact's last name |
| Mobile # | Contact's mobile phone number (must be unique) |
| Email | Contact's email address (must be unique) |

| Button | Action |
|---|---|
| Save | Insert a new contact or update an existing one |
| Search | Find a contact by mobile number or email |
| Delete | Remove the currently loaded contact |
| Reset | Clear all fields and return to the default state |

#### Requirements

```
pyodbc
ttkbootstrap
```

Install dependencies:

```bash
pip install pyodbc ttkbootstrap
```

#### Database Setup

The application uses **Microsoft SQL Server** via the ODBC Driver 17. Run the provided SQL script to create the required table, constraints, indexes, and stored procedures:

```bash
# Connect to your SQL Server instance and run:
SQL_Script/ContactBook.sql
```

The script creates:

- `Contact` table with `id`, `fname`, `lname`, `mnumber`, `maddress` columns
- Primary key and unique constraints on `mnumber` and `maddress`
- `SaveContact` stored procedure (insert or update)
- `DeleteContact` stored procedure
- `SearchContact` stored procedure

#### Configuration

The SQL Server connection string is defined as a class variable in `Contact.py`. Update it to match your environment:

```python
__sql_connection = 'DRIVER={ODBC Driver 17 for SQL Server};SERVER=<your-server>;DATABASE=<your-db>;UID=<username>;PWD=<password>'
```

> **Security note:** do not commit real server names, user names, or passwords. Prefer Windows authentication (`Trusted_Connection=yes`) or read the connection string from an environment variable in your own copy.

#### Usage

From the `GUI_Apps` folder:

```bash
python ContactBook/V1/Contact.py
```

#### FAQ

**Which ODBC driver do I need?**
The connection string uses `ODBC Driver 17 for SQL Server`. If you have a newer driver installed, such as ODBC Driver 18, change the `DRIVER` value to match.

**Why does saving fail for a contact that looks new?**
The database enforces unique mobile numbers and email addresses, so a save is rejected if either value already belongs to another contact.

---

## Folder Structure

```
GUI_Apps/
├── ContactBook/
│   └── V1/
│       └── Contact.py       # Main application
└── SQL_Script/
    └── ContactBook.sql      # Database schema and stored procedures
```

## Related

- [Text2Audio](../Text2Audio/readme.md) and [Setup Wizard — Fruit Wiki](../SetupWizard/readme.md) — more Python desktop GUI examples
- [Complete SQL Guide](https://github.com/gcfernando/document/blob/main/sql_complete_guide.md) — learn the SQL Server concepts used here, including stored procedures and constraints
- [Back to all Python projects](../README.md)

---

## Documentation links

[Read all Python Projects and Code Examples guides online](https://gcfernando.github.io/python_codes/documentation/) · [Project overview](https://gcfernando.github.io/python_codes/) · [All developer projects](https://gcfernando.github.io/gcfernando/projects/)
