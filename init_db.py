# init_db.py
# Replace 'streamlit_app' with your actual filename (without the .py extension)
from app_ui import app, db  

with app.app_context():
    db.create_all()
    print("Database tables created successfully!")