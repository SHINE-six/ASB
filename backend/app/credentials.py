import os
import getpass

def get_credentials():
    username = os.getenv("LINKEDIN_USERNAME", "")
    password = os.getenv("LINKEDIN_PASSWORD", "")
    if not username or not password:
      # try prompting for credentials if not set
      username = input("Enter your LinkedIn username: ").strip()
      password = getpass.getpass("Enter your LinkedIn password: ").strip()
    if not username or not password:
        raise ValueError("Missing LinkedIn credentials")
    return username, password
