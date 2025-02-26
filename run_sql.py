from app_ui import app, db
from sqlalchemy import text

# Function to run SQL commands from a file
def run_sql_file(filename):
    with app.app_context():
        with open(filename, 'r') as file:
            sql_commands = file.read()
            # Split commands if there are multiple (optional, based on your file structure)
            commands = sql_commands.split(';')
            for command in commands:
                if command.strip():  # Check if the command is not empty
                    db.session.execute(text(command))
            db.session.commit()  # Commit the changes to the database
            print("SQL commands executed successfully!")

# Specify the path to your .sql file
run_sql_file('chatdemo.sql')
