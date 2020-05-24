import json

from bson import ObjectId
from typing import List, Dict
from datetime import datetime
from dataclasses import dataclass, field

from app import db


files_db = db.files_db


@dataclass
class FileModel:
    _id: ObjectId
    file_owner: ObjectId
    filename: str
    systems_name: str


    @classmethod
    async def create_file(cls, file_owner: ObjectId, filename: str, systems_name: str):
        new_file = {
            "file_owner": file_owner,
            "filename": filename,
            "systems_name": systems_name
        }

        inserted = await files_db.insert_one(new_file)
        new_file['_id'] = inserted.inserted_id

        return cls(**new_file)

    @classmethod
    async def get_file(cls, file_id: ObjectId):
        file_record = await files_db.find_one(file_id)
        if file_record is None:
            raise ValueError("No such file")

        return cls(**file_record)
