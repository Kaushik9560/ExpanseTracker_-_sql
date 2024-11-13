import sqlite3

class ExpenseTracker:
    def __init__(self):
        # Connect to the SQLite database (or create it if it doesn't exist)
        self.conn = sqlite3.connect('expenses.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                amount REAL NOT NULL,
                category_id INTEGER,
                FOREIGN KEY (category_id) REFERENCES categories(id)
            )
        ''')
        self.conn.commit()
    
    def add_expense(self, date, amount, category):
        # Check if category exists, if not add it
        category_id = self.get_category_id(category)
        if category_id is None:
            category_id = self.add_category(category)

        # Insert expense into the database
        self.cursor.execute('''
            INSERT INTO expenses (date, amount, category_id)
            VALUES (?, ?, ?)
        ''', (date, amount, category_id))
        self.conn.commit()
    
    def add_category(self, category):
        try:
            self.cursor.execute('''
                INSERT INTO categories (name)
                VALUES (?)
            ''', (category,))
            self.conn.commit()
            print(f"Category '{category}' added.")
        except sqlite3.IntegrityError:
            print(f"Category '{category}' already exists.")

        return self.get_category_id(category)

    def get_category_id(self, category):
        self.cursor.execute('''
            SELECT id FROM categories WHERE name = ?
        ''', (category,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def view_expenses(self):
        self.cursor.execute('''
            SELECT categories.name, SUM(expenses.amount)
            FROM expenses
            JOIN categories ON expenses.category_id = categories.id
            GROUP BY categories.name
        ''')
        expenses = self.cursor.fetchall()
        for category, total_amount in expenses:
            print(f"{category}: ${total_amount:.2f}")

    def view_categories(self):
        self.cursor.execute('SELECT name FROM categories')
        categories = self.cursor.fetchall()
        print("Categories:")
        for (category,) in categories:
            print(category)

    def close(self):
        self.conn.close()


# Sample usage
tracker = ExpenseTracker()

while True:
    print("\nExpense Tracker Menu:")
    print("1. Add Expense")
    print("2. Add Category")
    print("3. View Expenses")
    print("4. View Categories")
    print("5. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        date = input("Enter date (YYYY-MM-DD): ")
        amount = float(input("Enter amount: $"))
        category = input("Enter category: ")
        tracker.add_expense(date, amount, category)
    elif choice == "2":
        category = input("Enter category: ")
        tracker.add_category(category)
    elif choice == "3":
        tracker.view_expenses()
    elif choice == "4":
        tracker.view_categories()
    elif choice == "5":
        tracker.close()
        print("Exiting Expense Tracker. Goodbye!")
        break
    else:
        print("Invalid choice. Please try again.")
