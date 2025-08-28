#!/usr/bin/env python3
"""
Debug script to analyze Outlook access token and check permissions
"""

import requests
import json
import base64
from urllib.parse import urlencode

def decode_jwt_token(token):
    """Decode JWT token to see its contents"""
    try:
        # Split the token
        parts = token.split('.')
        if len(parts) != 3:
            return None
        
        # Decode the payload (second part)
        payload = parts[1]
        # Add padding if needed
        payload += '=' * (4 - len(payload) % 4)
        
        # Decode base64
        decoded = base64.b64decode(payload)
        return json.loads(decoded)
    except Exception as e:
        print(f"Error decoding token: {e}")
        return None

def test_user_info_endpoint(access_token):
    """Test the Microsoft Graph user info endpoint"""
    url = "https://graph.microsoft.com/v1.0/me"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.ok:
            user_data = response.json()
            print(f"✅ Success! User data: {json.dumps(user_data, indent=2)}")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def main():
    print("Outlook Token Debug Tool")
    print("=" * 50)
    
    # Get token from user input
    token = input("Enter your access token (or press Enter to skip): ").strip()
    
    if token:
        print("\n1. Analyzing JWT Token...")
        token_data = decode_jwt_token(token)
        
        if token_data:
            print("✅ Token decoded successfully!")
            print(f"Token type: {token_data.get('typ', 'Unknown')}")
            print(f"Algorithm: {token_data.get('alg', 'Unknown')}")
            print(f"Audience: {token_data.get('aud', 'Unknown')}")
            print(f"Issuer: {token_data.get('iss', 'Unknown')}")
            print(f"Subject: {token_data.get('sub', 'Unknown')}")
            print(f"Expires: {token_data.get('exp', 'Unknown')}")
            
            # Check scopes
            scopes = token_data.get('scp', token_data.get('scope', ''))
            if isinstance(scopes, str):
                scopes = scopes.split(' ')
            print(f"Scopes: {scopes}")
            
            # Check if User.Read is present
            if 'User.Read' in scopes:
                print("✅ User.Read scope is present")
            else:
                print("❌ User.Read scope is missing!")
                print("This is likely the cause of the 403 error.")
        else:
            print("❌ Failed to decode token")
    
    print("\n2. Testing Microsoft Graph API...")
    if token:
        test_user_info_endpoint(token)
    else:
        print("Skipping API test (no token provided)")
    
    print("\n3. Troubleshooting Steps:")
    print("If you're getting 403 errors:")
    print("1. Go to Azure Portal > App Registrations > Your App > API Permissions")
    print("2. Add 'User.Read' permission if not present")
    print("3. Click 'Grant admin consent'")
    print("4. Make sure the OAuth scopes include 'User.Read'")
    print("5. Try the OAuth flow again")

if __name__ == "__main__":
    main()
