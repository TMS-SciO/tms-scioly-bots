from __future__ import annotations

import os
from typing import Any, Dict, List, TYPE_CHECKING

import motor.motor_asyncio
from dotenv import load_dotenv

if TYPE_CHECKING:
    from bot import TMS

load_dotenv()


class MongoDatabase:
    """
    Class for allowing the bot access to an external MongoDB database.
    """

    client: motor.motor_asyncio.AsyncIOMotorClient

    def __init__(self, bot: TMS):
        self.bot = bot

    async def setup(self):
        self.client = motor.motor_asyncio.AsyncIOMotorClient(
            os.getenv("MONGO_URL"), tz_aware=True
        )

    async def delete(self, db_name, collection_name, iden):
        collection = self.client[db_name][collection_name]
        await collection.delete_one({"_id": iden})

    async def get_entire_collection(
        self, db_name: str, collection_name: str, return_one=False
    ):

        collection = self.client[db_name][collection_name]
        if return_one:
            ret: dict = await collection.find_one()
            return ret
        result: list[dict] = []
        async for doc in collection.find():
            result.append(doc)
        return result

    async def get_cron(self) -> List:
        cron_list: List = await self.get_entire_collection("bot", "cron")
        return cron_list

    async def get_stealfish_ban(self) -> List:
        ret: dict = await self.get_entire_collection(
            "bot", "stealfishban", return_one=True
        )
        return ret["ids"]

    async def get_pings(self) -> List:
        ret = await self.get_entire_collection("bot", "pings")
        return ret

    async def get_censor(self) -> Dict[str, List[str]]:
        return await self.get_entire_collection("bot", "censor", return_one=True)

    async def insert(self, db_name, collection_name, insert_dict: Dict) -> None:
        collection = self.client[db_name][collection_name]
        return await collection.insert_one(insert_dict)

    async def update(self, db_name, collection_name, doc_id, update_dict: Dict) -> None:
        collection = self.client[db_name][collection_name]
        await collection.update_one({"_id": doc_id}, update_dict)

    async def update_many(
        self, db_name, collection_name, docs, update_dict: Dict
    ) -> None:
        collection = self.client[db_name][collection_name]
        ids = [doc.get("_id") for doc in docs]
        await collection.update_many({"_id": {"$in": ids}}, update_dict)

    async def remove_doc(self, db_name, collection_name, doc_id) -> None:
        collection = self.client[db_name][collection_name]
        await collection.delete_one({"_id": doc_id})
