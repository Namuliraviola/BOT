import streamlit as st
import requests
import json
import uuid
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import sessionmaker
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import OperationalError
import os

# Database connection URL
DATABASE_URL = "postgresql://viola_namulira_user:ewTcgq3M9peveLxRzJHwEmS2fRgwBxos@dpg-cuv3d49u0jms739f85t0-a.oregon-postgres.render.com/viola_namulira"

# Define Flask app and database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    __tablename__ = 'user'  # Ensure the table name is explicitly defined
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    license_file = db.Column(db.String(100), nullable=False)
    approved = db.Column(db.Boolean, default=False)

# Create the database tables if they don't exist
with app.app_context():
    try:
        db.create_all()
    except OperationalError as e:
        st.error(f"Database error: {e}")

# Connect to the database
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def get_db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

# Function to send messages to the chatbot API
def send_message(user_id, message):
    try:
        response = requests.post(
            "http://127.0.0.1:8501/chat",
            headers={"Content-Type": "application/json"},
            data=json.dumps({"user_id": user_id, "message": message}),
            timeout=5
        )
        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as e:
        st.error(f"Error communicating with chatbot API: {e}")
        return None

# Streamlit UI Setup
st.title("KETI AI")
st.write("get specailised health care for your patients online?.")

# Generate unique user ID
if "user_id" not in st.session_state:
    st.session_state["user_id"] = str(uuid.uuid4())

# Handle user registration
def save_user_info_to_db(user_info):
    session = SessionLocal()
    try:
        new_user = User(
            name=user_info['name'],
            email=user_info['email'],
            phone=user_info['phone'],
            user_type=user_info['type'],
            license_file=user_info['license_doc']  # Save the filename or path
        )
        session.add(new_user)
        session.commit()
        st.success("User information saved to the database.")
    except Exception as e:
        session.rollback()  # Rollback the session in case of an error
        st.error(f"Error saving user information: {e}")
    finally:
        session.close()

# Main logic for user registration
def handle_registration():
    if "step" not in st.session_state:
        st.session_state["step"] = 0
    if "user_info" not in st.session_state:
        st.session_state["user_info"] = {}

    if st.session_state["step"] == 0:
        registration_type = st.selectbox("Select Registration Type:", ["Select an entity", "Doctor", "Health Facility", "Hospital"])
        if registration_type != "Select an entity":
            st.session_state["user_info"]["type"] = registration_type.lower()
            st.session_state["step"] = 1
            st.rerun()

    elif st.session_state["step"] == 1:
        name = st.text_input("Name:")
        if st.button("Next"):
            if name.strip():
                st.session_state["user_info"]["name"] = name.strip()
                st.session_state["step"] = 2
                st.rerun()
            else:
                st.warning("Please enter a valid name.")

    elif st.session_state["step"] == 2:
        email = st.text_input("Email:")
        if st.button("Next"):
            if email.strip():
                st.session_state["user_info"]["email"] = email.strip()
                st.session_state["step"] = 3
                st.rerun()
            else:
                st.warning("Please enter a valid email address.")

    elif st.session_state["step"] == 3:
        phone = st.text_input("Phone Number:")
        if st.button("Next"):
            if phone.strip():
                st.session_state["user_info"]["phone"] = phone.strip()
                st.session_state["step"] = 4
                st.rerun()
            else:
                st.warning("Please enter a valid phone number.")

    elif st.session_state["step"] == 4:
        license_doc = st.file_uploader("Upload License Document (PDF):", type=["pdf"])
        if st.button("Submit"):
            if license_doc:
                license_file_path = f"uploads/{license_doc.name}"
                os.makedirs(os.path.dirname(license_file_path), exist_ok=True)  # Create uploads directory if it doesn't exist
                with open(license_file_path, "wb") as f:
                    f.write(license_doc.getbuffer())
                st.session_state["user_info"]["license_doc"] = license_file_path  # Save the file path
                save_user_info_to_db(st.session_state["user_info"])
                st.success("Registration successful!")
                st.session_state["step"] = 5
                st.rerun()
            else:
                st.warning("Please upload the license document.")

    elif st.session_state["step"] == 5:
        st.success("Registration completed!")
        if st.button("Register another entity"):
            st.session_state["step"] = 0
            st.session_state["user_info"] = {}
            st.rerun()

handle_registration()
