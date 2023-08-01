from motor.motor_asyncio import AsyncIOMotorClient


def create_db(db_uri: str, db_name):
    client_ = AsyncIOMotorClient(db_uri, connect=False)
    db_ = getattr(client_, db_name)
    return db_
