import json
import logging
from starlette.websockets import WebSocketState

logger = logging.getLogger(__name__)

async def broadcast_new_email(company_email_ws_clients, company_id: int, email_data: dict):
    logger.debug("ENTER broadcast_new_email for company %s", company_id)

    clients = company_email_ws_clients.get(company_id, [])
    if not clients:
        logger.debug("No clients connected for company %s", company_id)
        return

    # Make a stable copy so we can safely remove from the original
    client_list = list(clients)
    message = json.dumps({"type": "new_email", "data": email_data})

    dead = []
    for ws in client_list:
        try:
            # Skip if socket isn’t connected anymore
            if (
                getattr(ws, "application_state", None) != WebSocketState.CONNECTED or
                getattr(ws, "client_state", None) != WebSocketState.CONNECTED
            ):
                dead.append(ws)
                continue

            await ws.send_text(message)

        except Exception as e:
            logger.debug('Error sending to client %s: %s', ws, e)
            # Mark this socket to be pruned
            dead.append(ws)

    # Prune closed/bad sockets from your registry
    if dead:
        try:
            # Support list or set — remove whatever we marked dead
            if isinstance(clients, list):
                company_email_ws_clients[company_id] = [w for w in clients if w not in dead]
            else:  # set or similar
                for w in dead:
                    clients.discard(w)
        except Exception as e:
            logger.warning("Failed pruning dead clients: %s", e)

    logger.debug("Broadcast done for company %s (sent=%d, pruned=%d)", company_id, len(client_list) - len(dead), len(dead))
