from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from fastapi import HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    client: MongoClient = None
    
    @classmethod
    def get_client(cls):
        if cls.client is None:
            mongodb_url = os.getenv("MONGODB_URL")
            cls.client = MongoClient(mongodb_url)
            try:
                cls.client.admin.command('ping')
            except ConnectionFailure:
                raise HTTPException(status_code=500, detail="MongoDB connection failed")
        return cls.client

db = Database()
