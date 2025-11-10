# Bad code with ALL types of issues

import sqlite3
from some_module import *  # BEST PRACTICE: Wildcard import

# SECURITY: Hardcoded credentials
password = "admin123"
api_key = "sk-1234567890abcdef"
SECRET_TOKEN = "my_secret_token"
aws_access_key = "AKIAIOSFODNN7EXAMPLE"

# BEST PRACTICE: Lambda assignment
calculate = lambda x, y: x + y

def login(username, user_password):
    # SECURITY: SQL injection
    # BEST PRACTICE: Print statement
    print("Logging in user")  
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE username='{username}' AND password='{user_password}'"
    cursor.execute(query)
    return cursor.fetchone()

def get_user_data(user_id):
    # PERFORMANCE: No connection pooling
    # BEST PRACTICE: Type comparison
    if type(user_id) == int:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=" + str(user_id))
        return cursor.fetchone()

def get_all_users():
    # PERFORMANCE: SELECT * and fetchall()
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users")
    return cursor.fetchall()

def process_users(data=[]):  # BEST PRACTICE: Mutable default argument
    # PERFORMANCE: N+1 query
    users = get_all_users()
    for user in users:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM orders WHERE user_id={user[0]}")
        orders = cursor.fetchall()

def risky_function(data):
    try:
        result = eval(data)  # SECURITY: eval()
        return result
    except:  # BEST PRACTICE: Bare except
        pass  # BEST PRACTICE: Unnecessary pass

# BEST PRACTICE: TODO comment
# TODO: Fix this function later

# BEST PRACTICE: Magic numbers
def calculate_price(quantity):
    if quantity > 100:  # Magic number
        return quantity * 15.99  # Magic number
    return quantity * 19.99  # Magic number

# BEST PRACTICE: Boolean comparison
def check_status(is_active):
    if is_active == True:  # Should just be: if is_active
        return "Active"

# BEST PRACTICE: len() in conditional
def process_list(items):
    if len(items) > 0:  # Should just be: if items
        print("Processing")

# QUALITY: Very long function
def very_long_function(p1, p2, p3, p4, p5):
    result = p1 + p2
    result = result * p3
    result = result / p4
    result = result - p5
    result = p1 + p2
    result = result * p3
    result = result / p4
    result = result - p5
    result = p1 + p2
    result = result * p3
    result = result / p4
    result = result - p5
    return result
