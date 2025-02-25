import requests

BASE_URL = 'http://127.0.0.1:8501/chat'

def send_message(user_id, message):
    """Send a message to the chatbot."""
    response = requests.post(
        BASE_URL,
        json={"user_id": user_id, "message": message}
    )
    return response.json()

def main():
    user_id = input("Enter user ID: ")
    
    while True:
        message = input("You: ")
        
        if message.lower() in ["exit", "quit"]:
            print("Exiting the chat.")
            break
        
        response = send_message(user_id, message)
        print("Bot:", response.get('response', response.get('error', 'An error occurred.')))

if __name__ == "__main__":
    main()
