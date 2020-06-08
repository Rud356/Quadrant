from dataclasses import dataclass

from bson import ObjectId

from app import db

files_db = db.files_db


@dataclass
class FileModel:
    _id: ObjectId
    file_name: str
    system_name: str

    @classmethod
    async def create_file(cls, file_name: str, system_name: str):
        new_file = {
            "file_name": file_name,
            "system_name": system_name
        }

        inserted = await files_db.insert_one(new_file)
        new_file['_id'] = inserted.inserted_id

        return cls(**new_file)

    @classmethod
    async def get_file(cls, system_name: str):
        file_record = await files_db.find_one(
            {"system_name": system_name}
        )
        if file_record is None:
            raise ValueError("No such file")

        return cls(**file_record)