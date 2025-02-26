from flask import Flask, request, jsonify, send_from_directory
import os
from rapidfuzz import fuzz
import logging
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)
CORS(app)

# Configure the SQLAlchemy database URI (use your actual database configuration)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///registration.db'  # Example with SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# In-memory storage for session data
user_sessions = {}

# Define valid registration types
valid_types = ["doctor", "health facility", "hospital"]

# Set up logging
logging.basicConfig(level=logging.INFO)

# Define the User model for the database
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    user_type = db.Column(db.String(50), nullable=False)
    license_file = db.Column(db.String(200), nullable=True)
    #approved = db.Column(db.Boolean, default=False)  # New field for approval status

with app.app_context(): 
    db.create_all()  # Create the database tables

def match_intent(user_message, options, threshold=80):
    """Match user input against a list of options with a similarity threshold."""
    for option in options:
        if fuzz.ratio(user_message.lower(), option.lower()) > threshold:
            return option
    return None

def send_email(recipient_email, user_info):
    """Send an email notification."""
    sender_email = os.getenv("EMAIL_USER")  # Get your email from environment variables
    sender_password = os.getenv("EMAIL_PASS")  # Get your email password from environment variables

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = "Registration Confirmation"

    body = f"""
    Dear {user_info['name']},

    Your registration as a {user_info['user_type']} has been successfully completed and is awaiting approval!

    Best Regards,
    KETI AI Team
    """
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:  # Use your email provider's SMTP server
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            app.logger.info("Email sent successfully.")
    except Exception as e:
        app.logger.error(f"Failed to send email: {str(e)}")

@app.route('/')
def home():
    return 'Welcome to KETI AI!'

@app.route('/chat', methods=['POST'])
def chat():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON."}), 400
        
        data = request.json
        user_id = data.get("user_id")
        user_message = data.get("message", "").strip().lower()

        if not user_id or not user_message:
            return jsonify({"error": "Invalid request. Provide a user ID and message."}), 400

        if user_id not in user_sessions:
            user_sessions[user_id] = {"step": 0, "info": {}, "type": None}

        session = user_sessions[user_id]

        if session["step"] == 0:
            matched_type = match_intent(user_message, valid_types)
            if matched_type:
                session["type"] = matched_type
                session["step"] = 1
                return jsonify({"response": f"What is the {matched_type}'s name?"})
            return jsonify({"response": "Would you like to register as a doctor, health facility, or hospital?"})

        elif session["step"] == 1:
            session["info"]["name"] = user_message
            session["step"] = 2
            return jsonify({"response": f"What is the {session['type']}'s email?"})

        elif session["step"] == 2:
            session["info"]["email"] = user_message
            session["step"] = 3
            return jsonify({"response": f"What is the {session['type']}'s phone number?"})

        elif session["step"] == 3:
            session["info"]["phone"] = user_message
            session["step"] = 4
            return jsonify({"response": f"Please upload the {session['type']}'s license document (PDF). Type 'uploaded' when done."})

        elif session["step"] == 4:
            if user_message == "uploaded":
                session["step"] = 5

                # Save to the database
                new_user = User(
                    name=session["info"]["name"],
                    email=session["info"]["email"],
                    phone=session["info"]["phone"],
                    user_type=session["type"],
                    license_file=user_sessions[user_id]['info'].get('license_file', '')  # Use the uploaded file path
                )
                db.session.add(new_user)
                db.session.commit()

                # Send email notification
                send_email(session["info"]["email"], session["info"])

                return jsonify({"response": f"{session['type'].capitalize()} registration completed! Awaiting approval. Do you want to register another entity?"})
            return jsonify({"response": "Please confirm once you have uploaded the document by typing 'uploaded'."})

        elif session["step"] == 5:
            matched_type = match_intent(user_message, valid_types)
            if matched_type:
                session["type"] = matched_type
                session["step"] = 1
                return jsonify({"response": f"What is the {matched_type}'s name?"})
            return jsonify({"response": "Thank you! If you need to register another entity, specify: doctor, health facility, or hospital."})

        return jsonify({"response": "Unexpected input. Please follow the registration process."})

    except Exception as e:
        app.logger.error(f"Error processing request: {str(e)}")
        return jsonify({"error": "An error occurred while processing your request."}), 500

@app.route('/upload_license', methods=['POST'])
def upload_license():
    user_id = request.form.get("user_id")
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file:
        upload_folder = 'uploads'
        os.makedirs(upload_folder, exist_ok=True)

        file_path = os.path.join(upload_folder, file.filename)
        file.save(file_path)

        user_sessions[user_id]['info']['license_file'] = file_path
        return jsonify({"success": "File uploaded successfully."}), 200

@app.route('/uploads/<path:filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

#@app.route('/approve_registration/<int:user_id>', methods=['POST'])
#def approve_registration(user_id):
    #"""Endpoint for admin to approve registrations."""
    #user = User.query.get(user_id)
    #if user:
        #user.approved = True
        #db.session.commit()
        #return jsonify({"message": f"User {user.name} has been approved."}), 200
    #return jsonify({"error": "User not found."}), 404

#@app.route('/reject_registration/<int:user_id>', methods=['POST'])
#def reject_registration(user_id):
    #"""Endpoint for admin to reject registrations."""
    #user = User.query.get(user_id)
    i#f user:
        #db.session.delete(user)
        #db.session.commit()
        #return jsonify({"message": f"User {user.name} has been rejected and removed."}), 200
    #return jsonify({"error": "User not found."}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8501, debug=True)
