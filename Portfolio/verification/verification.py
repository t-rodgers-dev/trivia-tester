import bcrypt
import re
import json

# Initialize dictionaries
user_database = {}
top_scores = {}

def register_user():
    while True:
        username = input("Please choose a username: ")
        if username in user_database:
            print("Username already exists. Please choose another.")
            return
        else:
            break
    while True: 
        password = input("Please choose a password: ")
        if validate_pw(password): 
            hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            user_database[username] = {
                "password" : hashed_password,
                "high_score" : 0
            }
            print(f"User '{username}' registered successfully.")
            break
        else:
            print("""Please ensure your password has at least:
                   1 special character, 
                  1 digit, 
                  1 uppercase letter, 
                  and at least 5 characters long. """)

def verify_user():
    username = input("\nEnter your username: ")
    if username not in user_database:
        print("Username not found.")
        return
    
    input_password = input("Enter your password: ")
    stored_data = user_database[username]
    hashed_password = stored_data["password"]

    if bcrypt.checkpw(input_password.encode(), hashed_password):
        print("Login successful.")
        return username
    else:
        print("Login unsuccessful.")

def validate_pw(password):
    has_digit = re.search(r"\d", password)
    has_uppercase = re.search(r"[A-Z]", password)
    has_special = re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)

    if has_digit and has_uppercase and has_special and len(password)>=5:
        return True
    else:
        return False




