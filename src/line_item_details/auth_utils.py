import hashlib
import base64
import requests
import sys
import json
import os
from dotenv import load_dotenv

load_dotenv()

username=os.environ.get("email")
plaintext_password=os.environ.get("plaintext_password")

def generate_jwt(username, plaintext_password):
    try:
        # Step 1: MD5 hash the password
        md5_hash = hashlib.md5(plaintext_password.encode()).hexdigest()
        
        # Step 2: Base64 encode the MD5 hash
        encoded_password = base64.b64encode(md5_hash.encode()).decode()
        
        # Step 3: Prepare authentication request
        auth_url = "https://expresso.colombiaonline.com/expresso/jwt/api/authenticate.htm"
        auth_body = {
            "username": username,
            "password": encoded_password
        }
        
        # Send request to generate JWT token
        response = requests.post(auth_url, json=auth_body)
        
        if response.status_code == 200:
            jwt_token = response.json().get("jwt")
            print("JWT Token generated successfully.")
            return jwt_token
        else:
            print("Failed to generate JWT token:", response.text)
            sys.exit(1)
    except Exception as e:
        print("Error generating JWT token:", str(e))
        sys.exit(1)

def fetch_package_details(jwt_token, expresso_id):
    try:
        package_url = "https://expresso.colombiaonline.com/expresso/jwt/api/packageDetails.htm"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {jwt_token}"
        }
        
        # Ensure expresso_id is an integer
        try:
            expresso_id = int(expresso_id)
        except (ValueError, TypeError):
            print(f"Warning: Could not convert expresso_id to integer: {expresso_id}")
          
        
        print(f"Using expresso_id: {expresso_id} (type: {type(expresso_id).__name__})")

        # Try different payload formats
        # Format 1: Direct string of the ID (this is what worked in order_details.py)
        package_body_1 = str(expresso_id)
        print("Attempting with payload format 1 (direct string):", package_body_1)
        
        response = requests.post(package_url, headers=headers, data=package_body_1)
        
        if response.status_code == 200 and "Invalid parameter" not in str(response.text):
            response_json = response.json()
            print("Package Details fetched successfully (format 1):")
            return response_json

        return response.json()
        
    except Exception as e:
        print("Error fetching package details:", str(e))
        sys.exit(1) 