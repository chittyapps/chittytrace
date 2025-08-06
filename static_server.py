
import http.server
import socketserver
import os
from pathlib import Path

PORT = 8080
DIRECTORY = "static"

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
        print(f"Serving static files from {DIRECTORY} at http://0.0.0.0:{PORT}")
        print(f"Landing page: http://0.0.0.0:{PORT}/index.html")
        httpd.serve_forever()
