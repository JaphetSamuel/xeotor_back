from pydbantic import Database
from client.main import tables as client_tables
from driver.main import tables as driver_tables


async def init_db():
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

await init_db()