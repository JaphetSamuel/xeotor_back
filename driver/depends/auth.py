from fastapi import Header, HTTPException
from driver.models.models import Driver


async def check_driver(token:str =Header(...) ):
    driver = await Driver.get(id=token)
    if driver is None:
        raise HTTPException(status_code=401, detail="Utilisazteur non identifié")

    return driver

async def case_driver_exist(driver: Driver):
    if await Driver.filter(email=driver.email) :
        raise HTTPException(status_code=401, detail="email existe déja")

    if await Driver.filter(email=driver.contact) :
        raise HTTPException(status_code=401, detail="contact existe déja")
