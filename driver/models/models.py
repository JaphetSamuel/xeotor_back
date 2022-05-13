from pydbantic import DataBaseModel, PrimaryKey
from typing import List, Optional
import uuid


def get_uuid():
    return str(uuid.uuid4())

class Driver(DataBaseModel):
    id:str = PrimaryKey(default=get_uuid)
    fullname: str
    email: str
    contact:str
    car_brand: str
    car_model: str
    car_number: str
    password: Optional[str] = None

    pc: str

    confirm_code:str = "2445"

    is_active:bool = True
    is_online:bool = False

    picture:str = None
    average_rate:float = None
