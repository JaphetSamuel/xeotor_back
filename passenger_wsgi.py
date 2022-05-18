import os
import sys
from main import app
from a2wsgi import ASGIMiddleware
from pydbantic import Database
from client.main import tables as client_tables
from driver.main import tables as driver_tables
import asyncio


async def init_bd():
    print("initialisaztion de la bd dans init")
    try:
        db = await Database.create(
            "sqlite:///./xeotor.db",
            tables=client_tables + driver_tables,
            redis_url="redis://localhost"
        )
    except Exception as e:
        print("erreur d'initialisationde la bd")
        print(e)
        print(e.args)

asyncio.run(init_bd())


application = ASGIMiddleware(app)


sys.path.insert(0, os.path.dirname(__file__))
