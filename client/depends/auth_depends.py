from client.models.models import Client, Commande
from fastapi import Header,HTTPException


#verifie si le client possedant client_id envoyé existe bien
async def check_client(client_id:str = Header(...)):
    client = await Client.get(id=client_id)
    if client is None:
        raise HTTPException(status_code=401,detail="client_id inconnu")
    return client