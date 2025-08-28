#!/usr/bin/env python3
"""
Simple SMTP test script for Gmail credentials verification.
Run this script to test your Gmail SMTP credentials independently.
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def test_gmail_smtp():
    # REPLACE THESE WITH YOUR ACTUAL CREDENTIALS
    smtp_server = "smtp.gmail.com"
    smtp_port = 587  # Use 465 for SSL instead of STARTTLS
    username = "YOUR_GMAIL@gmail.com"  # Replace with your Gmail
    password = "YOUR_APP_PASSWORD"     # Replace with your 16-char App Password
    
    # Test recipient (can be same as sender for testing)
    to_email = "YOUR_GMAIL@gmail.com"
    
    print(f"Testing Gmail SMTP connection...")
    print(f"Server: {smtp_server}:{smtp_port}")
    print(f"Username: {username}")
    print(f"Password: {password[:4]}{'*' * (len(password) - 4)}")
    print("-" * 50)
    
    try:
        # Create message
        msg = MIMEMultipart()
        msg['From'] = username
        msg['To'] = to_email
        msg['Subject'] = "SMTP Test Email"
        
        body = "This is a test email to verify Gmail SMTP credentials."
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect and send
        print("Connecting to Gmail SMTP server...")
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        print("Starting TLS...")
        server.starttls()  # Enable security
        
        print("Logging in...")
        server.login(username, password)
        
        print("Sending email...")
        text = msg.as_string()
        server.sendmail(username, to_email, text)
        
        print("Closing connection...")
        server.quit()
        
        print("✅ SUCCESS: Email sent successfully!")
        print("Your Gmail SMTP credentials are working correctly.")
        
    except smtplib.SMTPAuthenticationError as e:
        print(f"❌ AUTHENTICATION ERROR: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Make sure you're using an App Password, not your regular Gmail password")
        print("2. Check that 2-Step Verification is enabled on your Google account")
        print("3. Visit: https://myaccount.google.com/apppasswords")
        print("4. Generate a new App Password for 'Mail' or 'Other (Custom name)'")
        
    except smtplib.SMTPConnectError as e:
        print(f"❌ CONNECTION ERROR: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify firewall/antivirus isn't blocking SMTP")
        print("3. Try using port 465 with SSL instead of 587 with STARTTLS")
        
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        print(f"Error type: {type(e).__name__}")

if __name__ == "__main__":
    print("Gmail SMTP Credential Test")
    print("=" * 50)
    test_gmail_smtp() 