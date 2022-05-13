from fastapi import APIRouter
from client.models.models import Client, Commande, Trajet

route = APIRouter(prefix="/commande", tags=['commandes'])

@route.get("/", response_model=list[Commande])
async def get_all_commndes():
    return await Commande.all()