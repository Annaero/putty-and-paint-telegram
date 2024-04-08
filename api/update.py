from http.server import BaseHTTPRequestHandler
import logging
import os


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()

        logging.log("Enter handler")

        return
