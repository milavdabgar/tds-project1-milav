import sqlite3

conn = sqlite3.connect('data/test.db')
c = conn.cursor()

# Create table
c.execute('''CREATE TABLE users
             (id INTEGER PRIMARY KEY,
              name TEXT,
              email TEXT)''')

# Insert data
c.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("John", "john@example.com"))
c.execute("INSERT INTO users (name, email) VALUES (?, ?)", ("Jane", "jane@example.com"))

# Save and close
conn.commit()
conn.close()
