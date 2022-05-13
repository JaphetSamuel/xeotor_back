from typing import Optional, Union, List
from pydbantic import DataBaseModel, PrimaryKey, Database
import uuid

def get_uuid():
    return str(uuid.uuid4())


class Trajet(DataBaseModel):
    id:str = PrimaryKey(default=get_uuid)

    polygone: List[List[float]] = []
    total_distance:Optional[float] = None
    total_duration:Optional[float] = None

    depart: list = []
    destination: list = []

    def calcule_prix(self):
        prix: int = int(self.total_distance / 2)
        return prix+10, prix + 200, prix + 500

    async def save(self, *args,**kwargs):
        return await super().save()



class Payment(DataBaseModel):
    id: str = PrimaryKey(default=get_uuid)
    is_cash:bool = True

class Client(DataBaseModel):
    id: Optional[str] = PrimaryKey(default=get_uuid,)
    fullname: str
    email: str
    contact: str
    password:Optional[str] = None

class Commande(DataBaseModel):

    id: Optional[str] = PrimaryKey(default=get_uuid)

    prix: Optional[int]
    client:Optional[Client] = None
    driver:Optional[str] = None #Pour l'instant
    payment: Optional[Payment] = None

    statut: str = "pending"
    flavour:Optional[str] = "share"
    note_client:Optional[int] = None
    note_driver:Optional[int] = None
    prix:Optional[int]

    trajet:Trajet

    sid: Optional[str] = None

    async def set_prix(self):
        share,private,luxe = self.trajet.calcule_prix()
        prix:int = 1
        print(self.flavour)
        if self.flavour == "share":
            prix = int(share)
        if self.flavour == "private":
            prix = int(private)
        if self.flavour == "luxe":
            prix = int(luxe)
        self.prix = prix
        await self.update()
        return self.prix

    def save(self, *args, **kwargs):
        self.set_prix()
        super().save()