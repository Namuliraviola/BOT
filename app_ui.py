import streamlit as st
import requests
import json
import uuid

# Function to send messages to the Flask chatbot API
def send_message(user_id, message):
    """Send a message to the chatbot."""
    response = requests.post(
        "http://127.0.0.1:8501/chat",
        headers={"Content-Type": "application/json"},
        data=json.dumps({"user_id": user_id, "message": message})
    )
    return response

# Set up the Streamlit app
st.title("Chatbot Registration")
st.write("Interact with the chatbot by entering your messages below.")

# Generate a unique user ID for the session
user_id = str(uuid.uuid4())

# Selection for registration type
registration_type = st.selectbox("Select Registration Type:", ["Select an entity", "Doctor", "Health Facility", "School"])

# Function to handle user inputs based on selected registration type
def handle_registration():
    if registration_type != "Select an entity":
        st.write(f"### Register a {registration_type}")

        # Collect user information
        name = st.text_input("Name:")
        email = st.text_input("Email:")
        phone = st.text_input("Phone Number:")
        license_doc = st.file_uploader("Upload License Document (PDF):", type=["pdf"])

        if st.button("Submit"):
            if name and email and phone and license_doc:
                # Prepare the message for the bot
                message = f"Register {registration_type.lower()}: {name}, {email}, {phone}, {license_doc.name}"

                # Send the user message to the Flask chatbot API
                response = send_message(user_id, message)

                # Handle the response from the chatbot
                if response.status_code == 200:
                    bot_response = response.json().get("response")
                    st.write(f"Chatbot: {bot_response}")
                else:
                    st.write("Error: Unable to get a response from the chatbot.")

                # Option to register another entity
                if st.button("Register Another Entity"):
                    reset_form()

            else:
                st.write("Please fill in all the fields and upload the license document.")

def reset_form():
    """Reset the form fields."""
    st.session_state['name'] = ""
    st.session_state['email'] = ""
    st.session_state['phone'] = ""
    st.session_state['license_doc'] = None
    st.experimental_rerun()

# Initialize session state variables
if 'name' not in st.session_state:
    st.session_state['name'] = ""
if 'email' not in st.session_state:
    st.session_state['email'] = ""
if 'phone' not in st.session_state:
    st.session_state['phone'] = ""
if 'license_doc' not in st.session_state:
    st.session_state['license_doc'] = None

# Display the registration form
handle_registration()
