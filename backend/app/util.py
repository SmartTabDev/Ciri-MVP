import re
from bs4 import BeautifulSoup

# Utility function to extract clean email address from Gmail header format.
def extract_email_address(email_header: str) -> str:
    if not email_header:
        return ""
    if '<' in email_header and '>' in email_header:
        start = email_header.find('<') + 1
        end = email_header.find('>')
        if start > 0 and end > start:
            return email_header[start:end].strip()
    return email_header.strip()

# Function to clean HTML content by removing specific <br> patterns
def clean_html_content(html_content: str) -> str:
    print(f"[DEBUG] Cleaning HTML content: {html_content}")
    # Remove <br> tags from specific patterns
    cleaned_content = re.sub(r'</div><br/>', '</div>', html_content)
    print(f"[DEBUG] Cleaned content after first substitution: {cleaned_content}")
    cleaned_content = re.sub(r'<div><br/></div>', '', cleaned_content)
    print(f"[DEBUG] Cleaned content after second substitution: {cleaned_content}")
    return cleaned_content

# Utility function to remove HTML parts with specific class.
def remove_gmail_quote(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    for quote in soup.find_all(class_='gmail_quote gmail_quote_container'):
        quote.decompose()
    return str(soup) 