#!/usr/bin/env python3
from http.server import HTTPServer, SimpleHTTPRequestHandler
import os
import sys

class MyHTTPRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        SimpleHTTPRequestHandler.end_headers(self)
    
    def log_message(self, format, *args):
        # Log vers stdout pour Railway
        sys.stdout.write("%s - - [%s] %s\n" %
                         (self.address_string(),
                          self.log_date_time_string(),
                          format%args))
        sys.stdout.flush()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    print(f'Starting server on 0.0.0.0:{port}', flush=True)
    
    try:
        server = HTTPServer(('0.0.0.0', port), MyHTTPRequestHandler)
        print(f'Server successfully started on port {port}', flush=True)
        print(f'Ready to accept connections', flush=True)
        server.serve_forever()
    except Exception as e:
        print(f'Error starting server: {e}', flush=True)
        sys.exit(1)
