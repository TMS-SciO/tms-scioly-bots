import asyncio
import os

import utils
import motor.motor_asyncio

client: motor.motor_asyncio.AsyncIOMotorClient


async def setup():
    global client
    client = motor.motor_asyncio.AsyncIOMotorClient(
        os.getenv("MONGO_URL")
    )


async def delete(db_name, collection_name, iden):
    global client
    collection = client[db_name][collection_name]
    await collection.delete_one({"_id": iden})


async def get_entire_collection(db_name, collection_name, return_one=False):
    global client
    collection = client[db_name][collection_name]
    if return_one:
        ret: dict = await collection.find_one()
        return ret
    result: list[dict] = []
    async for doc in collection.find():
        result.append(doc)
    return result


async def get_cron() -> list:
    cron_list: list = await get_entire_collection("bot", "cron")
    return cron_list


async def get_stealfish_ban() -> list:
    ret: dict = await get_entire_collection("bot", "stealfishban", return_one=True)
    return ret["ids"]


async def get_pings() -> list:
    ret = await get_entire_collection("bot", "pings")
    return ret


async def get_censor() -> dict[str, list[str]]:
    global client
    return await get_entire_collection("bot", "censor", return_one=True)


async def insert(db_name, collection_name, insert_dict):
    global client
    collection = client[db_name][collection_name]
    return await collection.insert_one(insert_dict)


async def update(db_name, collection_name, doc_id, update_dict):
    global client
    collection = client[db_name][collection_name]
    await collection.update_one({'_id': doc_id}, update_dict)


async def update_many(db_name, collection_name, docs, update_dict):
    global client
    collection = client[db_name][collection_name]
    ids = [doc.get("_id") for doc in docs]
    await collection.update_many(
        {"_id": {
            "$in": ids
        }
        },
        update_dict
    )


async def remove_doc(db_name, collection_name, doc_id):
    global client
    collection = client[db_name][collection_name]
    await collection.delete_one({'_id': doc_id})


event_loop = asyncio.get_event_loop()
# asyncio.ensure_future(setup(), loop = event_loop)
event_loop.run_until_complete(setup())
