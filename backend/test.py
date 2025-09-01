import requests
BASE = "https://graph.instagram.com/v23.0"
TOKEN = "IGAAP0F6RECdRBZAE5NZATdCVGFXVDN6ZAEhpYUw3TWR6ZATFjTUpfajVnMWNaTlRLdlZAHUUlucEJQX3YwMno1bTN1a203b3pHaWtkY2hLOFRlWGJMLUVkejhRRDlEVnI2QWQ3a1dHU00wRXV3ZAjhjUDAwb2FjTnBpZAFBKZAUIyOG5uUmZAmRnZAxNVFUZAUhOakIxcTV6bjRQYwZDZD"

me = requests.get(f"{BASE}/me", params={"fields":"id,username,account_type","access_token":TOKEN}).json()
print("ME:", me)

ig_id = me.get("id")
convs = requests.get(f"{BASE}/{ig_id}/conversations", params={"limit":20,"access_token":TOKEN}).json()
print("CONVERSATIONS:", convs)
