import json

async def broadcast_new_email(company_email_ws_clients, company_id: int, email_data: dict):
    print("!!! [DEBUG] ENTER broadcast_new_email for company", company_id)
    clients = company_email_ws_clients.get(company_id, [])
    print(f"[DEBUG] Number of clients to broadcast: {len(clients)}")
    if not clients:
        print(f"[DEBUG] No clients connected for company {company_id}")
        return
    message = json.dumps({"type": "new_email", "data": email_data})
    for ws in clients:
        try:
            print(f"[DEBUG] Sending email to client {ws}")
            await ws.send_text(message)
        except Exception as e:
            print(f"[DEBUG] Error sending to client: {e}")
            pass  # Ignore errors for now 