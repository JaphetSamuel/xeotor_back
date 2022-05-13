from fastapi_events.typing import Event
from fastapi_events.handlers.local import local_handler

######### TEST ###########

@local_handler.register(event_name="check_all")
async def handler(event:Event):
    event_name, payload = event
    print(f"client handlers.py : un event recu {event_name} parms: {payload['val']}")

################