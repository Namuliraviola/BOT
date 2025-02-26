# database_viewer.py
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd

# Import your app and models - adjust the import according to your app's filename
# This assumes your main file is in the same directory and named 'streamlit_app.py'
try:
    # Try to import the app and database model from your main file
    # Replace 'streamlit_app' with your actual file name (without .py)
    from app_ui import app, db, User
except ImportError as e:
    print(f"Error importing your app: {e}")
    print("Please update the import statement in this file to match your app's filename.")
    sys.exit(1)

def list_all_users():
    """Display all users in the database"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in the database.")
            return
        
        print("\n=== ALL USERS ===")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Phone: {user.phone}")
            print(f"Type: {user.user_type}")
            print(f"License File: {user.license_file}")
            print("-" * 40)

def search_user(field, value):
    """Search for users by a specific field and value"""
    with app.app_context():
        query = None
        
        # Create the appropriate query based on the field
        if field == 'id':
            query = User.query.filter(User.id == value)
        elif field == 'name':
            query = User.query.filter(User.name.like(f"%{value}%"))
        elif field == 'email':
            query = User.query.filter(User.email.like(f"%{value}%"))
        elif field == 'phone':
            query = User.query.filter(User.phone.like(f"%{value}%"))
        elif field == 'type':
            query = User.query.filter(User.user_type.like(f"%{value}%"))
        else:
            print(f"Invalid field: {field}")
            return
        
        users = query.all()
        
        if not users:
            print(f"No users found matching {field}={value}")
            return
        
        print(f"\n=== SEARCH RESULTS: {field}={value} ===")
        for user in users:
            print(f"ID: {user.id}")
            print(f"Name: {user.name}")
            print(f"Email: {user.email}")
            print(f"Phone: {user.phone}")
            print(f"Type: {user.user_type}")
            print(f"License File: {user.license_file}")
            print("-" * 40)

def delete_user(user_id):
    """Delete a user by ID"""
    with app.app_context():
        user = User.query.get(user_id)
        
        if not user:
            print(f"No user found with ID: {user_id}")
            return
        
        # Confirm deletion
        confirm = input(f"Are you sure you want to delete user {user.name} (ID: {user.id})? (y/n): ")
        
        if confirm.lower() == 'y':
            db.session.delete(user)
            db.session.commit()
            print(f"User {user.name} (ID: {user.id}) deleted successfully.")
        else:
            print("Deletion cancelled.")

def export_to_csv():
    """Export all users to a CSV file"""
    with app.app_context():
        users = User.query.all()
        
        if not users:
            print("No users found in the database.")
            return
        
        # Convert to list of dictionaries
        user_data = []
        for user in users:
            user_data.append({
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'phone': user.phone,
                'user_type': user.user_type,
                'license_file': user.license_file
            })
        
        # Create DataFrame and export to CSV
        df = pd.DataFrame(user_data)
        filename = 'users_export.csv'
        df.to_csv(filename, index=False)
        print(f"Users exported to {filename} successfully.")

def add_user():
    """Add a new user manually"""
    print("\n=== ADD NEW USER ===")
    
    name = input("Name: ")
    email = input("Email: ")
    phone = input("Phone: ")
    user_type = input("User Type (doctor/hospital/health facility): ")
    license_file = input("License File (filename): ")
    
    # Validate inputs
    if not all([name, email, phone, user_type, license_file]):
        print("All fields are required. User not added.")
        return
    
    with app.app_context():
        new_user = User(
            name=name,
            email=email,
            phone=phone,
            user_type=user_type,
            license_file=license_file
        )
        
        db.session.add(new_user)
        db.session.commit()
        print(f"User {name} added successfully with ID: {new_user.id}")

def display_menu():
    """Display the main menu"""
    print("\n=== DATABASE VIEWER ===")
    print("1. List all users")
    print("2. Search for users")
    print("3. Add a new user")
    print("4. Delete a user")
    print("5. Export all users to CSV")
    print("6. Quit")
    
    choice = input("\nEnter your choice (1-6): ")
    return choice

def main():
    while True:
        choice = display_menu()
        
        if choice == '1':
            list_all_users()
        elif choice == '2':
            print("\n--- Search Options ---")
            print("1. ID")
            print("2. Name")
            print("3. Email")
            print("4. Phone")
            print("5. User Type")
            
            search_choice = input("Search by (1-5): ")
            field_map = {
                '1': 'id',
                '2': 'name',
                '3': 'email',
                '4': 'phone',
                '5': 'type'
            }
            
            if search_choice in field_map:
                value = input(f"Enter {field_map[search_choice]} to search for: ")
                search_user(field_map[search_choice], value)
            else:
                print("Invalid choice.")
        elif choice == '3':
            add_user()
        elif choice == '4':
            user_id = input("Enter the ID of the user to delete: ")
            try:
                user_id = int(user_id)
                delete_user(user_id)
            except ValueError:
                print("Please enter a valid numeric ID.")
        elif choice == '5':
            export_to_csv()
        elif choice == '6':
            print("Exiting database viewer.")
            break
        else:
            print("Invalid choice. Please enter a number from 1 to 6.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting database viewer.")
    except Exception as e:
        print(f"An error occurred: {e}")