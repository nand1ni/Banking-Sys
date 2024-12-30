import mysql.connector
from mysql.connector import Error
import re
import random
from getpass import getpass

def create_connection():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_password',
            database='banking_system'
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error: {e}")
        return None

def create_tables(connection):
    cursor = connection.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) NOT NULL,
        account_number VARCHAR(10) UNIQUE NOT NULL,
        dob DATE NOT NULL,
        city VARCHAR(50) NOT NULL,
        password VARCHAR(200) NOT NULL,
        balance FLOAT DEFAULT 2000,
        contact_number VARCHAR(10) UNIQUE NOT NULL,
        email VARCHAR(100) UNIQUE NOT NULL,
        address VARCHAR(200) NOT NULL,
        active BOOLEAN DEFAULT TRUE
    )''')
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transaction (
        id INT AUTO_INCREMENT PRIMARY KEY,
        account_number VARCHAR(10) NOT NULL,
        type VARCHAR(10) NOT NULL,
        amount FLOAT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )''')
    connection.commit()

def is_valid_email(email):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

def is_valid_contact_number(number):
    return re.match(r"^\d{10}$", number)

def is_valid_password(password):
    return re.match(r"^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*?&]{8,}$", password)

def generate_account_number(connection):
    cursor = connection.cursor()
    while True:
        account_number = ''.join(random.choices('0123456789', k=10))
        cursor.execute("SELECT * FROM users WHERE account_number = %s", (account_number,))
        if not cursor.fetchone():
            return account_number

def add_user(connection):
    cursor = connection.cursor()
    name = input("Enter name: ")
    dob = input("Enter date of birth (YYYY-MM-DD): ")
    city = input("Enter city: ")
    while True:
        email = input("Enter email: ")
        if is_valid_email(email):
            break
        print("Invalid email address.")
    while True:
        contact_number = input("Enter contact number: ")
        if is_valid_contact_number(contact_number):
            break
        print("Invalid contact number.")
    while True:
        password = getpass("Enter password: ")
        if is_valid_password(password):
            break
        print("Password must contain at least 8 characters, including letters and numbers.")
    address = input("Enter address: ")
    initial_balance = max(2000, float(input("Enter initial balance (minimum 2000): ")))

    account_number = generate_account_number(connection)

    cursor.execute('''INSERT INTO users (name, account_number, dob, city, password, balance, contact_number, email, address) 
                      VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                   (name, account_number, dob, city, password, initial_balance, contact_number, email, address))
    connection.commit()
    print(f"User added successfully. Account Number: {account_number}")

def show_users(connection):
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    for user in users:
        print(f"Name: {user[1]}, Account Number: {user[2]}, Balance: {user[6]}")

def login(connection):
    cursor = connection.cursor()
    account_number = input("Enter account number: ")
    password = getpass("Enter password: ")
    cursor.execute("SELECT * FROM users WHERE account_number = %s AND password = %s", (account_number, password))
    user = cursor.fetchone()
    if user:
        print(f"Welcome {user[1]}!")
        user_dashboard(connection, account_number)
    else:
        print("Invalid account number or password.")

def user_dashboard(connection, account_number):
    while True:
        print("\n1. Show Balance\n2. Credit Amount\n3. Debit Amount\n4. Exit")
        choice = input("Enter choice: ")
        if choice == '1':
            show_balance(connection, account_number)
        elif choice == '2':
            credit_amount(connection, account_number)
        elif choice == '3':
            debit_amount(connection, account_number)
        elif choice == '4':
            break
        else:
            print("Invalid choice.")

def show_balance(connection, account_number):
    cursor = connection.cursor()
    cursor.execute("SELECT balance FROM users WHERE account_number = %s", (account_number,))
    balance = cursor.fetchone()[0]
    print(f"Your balance is: {balance}")

def credit_amount(connection, account_number):
    cursor = connection.cursor()
    amount = float(input("Enter amount to credit: "))
    cursor.execute("UPDATE users SET balance = balance + %s WHERE account_number = %s", (amount, account_number))
    cursor.execute("INSERT INTO transaction (account_number, type, amount) VALUES (%s, %s, %s)", (account_number, 'credit', amount))
    connection.commit()
    print("Amount credited successfully.")

def debit_amount(connection, account_number):
    cursor = connection.cursor()
    amount = float(input("Enter amount to debit: "))
    cursor.execute("SELECT balance FROM users WHERE account_number = %s", (account_number,))
    balance = cursor.fetchone()[0]
    if amount > balance:
        print("Insufficient balance.")
    else:
        cursor.execute("UPDATE users SET balance = balance - %s WHERE account_number = %s", (amount, account_number))
        cursor.execute("INSERT INTO transaction (account_number, type, amount) VALUES (%s, %s, %s)", (account_number, 'debit', amount))
        connection.commit()
        print("Amount debited successfully.")

def main():
    connection = create_connection()
    if connection:
        create_tables(connection)
        while True:
            print("\n1. Add User\n2. Show Users\n3. Login\n4. Exit")
            choice = input("Enter choice: ")
            if choice == '1':
                add_user(connection)
            elif choice == '2':
                show_users(connection)
            elif choice == '3':
                login(connection)
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice.")
        connection.close()

if __name__ == "__main__":
    main()
