import requests
import time
import os
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler

# Bot Token from environment variable
TOKEN = os.environ.get('BOT_TOKEN')
if not TOKEN:
    print("❌ Error: BOT_TOKEN not found in environment variables!")
    exit(1)

API_URL = f"https://api.telegram.org/bot{TOKEN}"

class HealthCheckHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Echo Bot is running!')
    
    def log_message(self, format, *args):
        pass

def run_web_server():
    port = int(os.environ.get('PORT', 10000))
    server = HTTPServer(('0.0.0.0', port), HealthCheckHandler)
    print(f"Web server running on port {port}")
    server.serve_forever()

def send_request(url, data, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.post(url, json=data, timeout=10)
            return response.json()
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(1)
    return None

def get_request(url, params, max_retries=3):
    for attempt in range(max_retries):
        try:
            response = requests.get(url, params=params, timeout=10)
            return response.json()
        except requests.exceptions.RequestException:
            if attempt < max_retries - 1:
                time.sleep(1)
    return None

def copy_message(chat_id, from_chat_id, message_id):
    """Copy any type of message to the same chat"""
    url = f"{API_URL}/copyMessage"
    data = {
        "chat_id": chat_id,
        "from_chat_id": from_chat_id,
        "message_id": message_id
    }
    return send_request(url, data)

def send_message(chat_id, text):
    """Send text message"""
    url = f"{API_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    return send_request(url, data)

def main():
    print("🤖 Echo Bot starting...")
    
    # Start web server in background
    web_thread = Thread(target=run_web_server, daemon=True)
    web_thread.start()
    
    offset = None
    while True:
        try:
            url = f"{API_URL}/getUpdates"
            updates = get_request(url, {"timeout": 30, "offset": offset})
            
            if updates and updates.get("ok"):
                for update in updates.get("result", []):
                    offset = update["update_id"] + 1
                    
                    if "message" in update:
                        message = update["message"]
                        chat_id = message["chat"]["id"]
                        message_id = message["message_id"]
                        
                        # Handle /start command
                        if "text" in message and message["text"] == "/start":
                            send_message(chat_id, "👋 স্বাগতম! আমি একটি Echo Bot।\n\nআপনি যা পাঠাবেন তাই আমি ফেরত পাঠাব - ছবি, ভিডিও, অডিও, ফাইল, টেক্সট সবকিছু!")
                        else:
                            # Echo back any message using copyMessage
                            copy_message(chat_id, chat_id, message_id)
                            
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()
