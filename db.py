import sqlite3
import csv
import os

# Define the database file path
db_path = r"C:\Users\DELL\Desktop\A.U.R.O.R.A\AURORA\aurora.db"

# Check if the database file exists and delete it if it's corrupted
if os.path.exists(db_path):
    try:
        # Try to connect to the database to check its integrity
        test_connection = sqlite3.connect(db_path)
        test_connection.execute("PRAGMA integrity_check;")
        test_connection.close()
    except sqlite3.DatabaseError:
        print("Database file is corrupted. Deleting the file and creating a new one.")
        os.remove(db_path)

# Connect to the database (it will create a new file if it doesn't exist)
connection = sqlite3.connect(db_path)

# Create a cursor object to execute SQL commands
cursor = connection.cursor()

# Create the contacts table if it doesn't exist
cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY,
                    name VARCHAR(200),
                    mobile_no VARCHAR(255),
                    email VARCHAR(255) NULL
                 )''')

# Specify the column indices you want to import (0-based index)
desired_columns_indices = [0, 18]  # Adjusted indices based on your CSV file

# Open the CSV file and read the data
csv_file_path = r"C:\Users\DELL\Desktop\A.U.R.O.R.A\AURORA\contacts.csv"
try:
    with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip the header row

        for row_number, row in enumerate(csvreader, start=1):
            if len(row) <= max(desired_columns_indices):
                print(f"Skipping row {row_number} due to insufficient columns: {row}")
                continue

            try:
                selected_data = [row[i] for i in desired_columns_indices]
                cursor.execute('''INSERT INTO contacts (id, name, mobile_no) VALUES (NULL, ?, ?);''', tuple(selected_data))
            except Exception as e:
                print(f"Error processing row {row_number}: {e}")

except FileNotFoundError:
    print(f"CSV file not found: {csv_file_path}")

# Commit changes after inserting data
connection.commit()
print("Data inserted successfully!")

# Remove duplicate entries by keeping only the first occurrence of each (name, mobile_no) pair
cursor.execute('''
    DELETE FROM contacts
    WHERE id NOT IN (
        SELECT MIN(id)
        FROM contacts
        GROUP BY name, mobile_no
    );
''')

# Commit the deletion of duplicates
connection.commit()
print("Duplicates removed successfully!")

# Define the search query (e.g., "kunal")
query = 'Yaseen'

# Sanitize the query to make it case-insensitive and remove any extra spaces
query = query.strip().lower()

# Execute the query to search for matching names in the contacts table
cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?",
               ('%' + query + '%', query + '%'))

# Fetch all the results from the query
results = cursor.fetchall()

# Check if there are any results and print the first mobile number
if results:
    print(f"First mobile number found: {results[0][0]}")
else:
    print("No results found.")

# Fetch and display all records from the contacts table
cursor.execute('''SELECT * FROM contacts''')
rows = cursor.fetchall()

print("\nDisplaying data from the contacts table:")
print("ID\tName\t\tMobile No\t\tEmail")
print("-" * 50)
if rows:
    for row in rows:
        id, name, mobile_no, email = row
        print(f"{id}\t{name}\t{mobile_no}\t{email if email else 'N/A'}")
else:
    print("No records found in the contacts table.")

# Close the database connection
connection.close()
