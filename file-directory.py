from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler

PORT = 8000
DIRECTORY = "/Users/phoelandsiu/audio-project"

# Change working directory to serve files from there
import os
os.chdir(DIRECTORY)

print(f"Serving {DIRECTORY} at http://localhost:{PORT}")
ThreadingHTTPServer(("0.0.0.0", PORT), SimpleHTTPRequestHandler).serve_forever()