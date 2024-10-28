import http.server
import socketserver
import os
import signal
import sys

# Define the port you want to serve on
PORT = 8000

# Get the directory where this script is located
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class RequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_GET(self):
        # Serve home_page.html for root URL '/'
        if self.path == "/":
            self.path = "/home_page.html"  # Change this to serve home_page.html
        return super().do_GET()

# Handle Ctrl + C to shut down gracefully
def signal_handler(sig, frame):
    print("Shutting down server...")
    sys.exit(0)

def run_server():
    # Set up signal handler to catch Ctrl + C
    signal.signal(signal.SIGINT, signal_handler)

    # Start the server
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        print(f"Serving at http://localhost:{PORT}")
        httpd.serve_forever()

if __name__ == "__main__":
    run_server()
