from fastapi import APIRouter, Body, Request, Response, HTTPException, status
from fastapi.encoders import jsonable_encoder
from typing import List
from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
import os
import uvicorn
from bson import json_util
import json
config = dotenv_values(".env")
MONGODB_ATLAS_CLUSTER_URI = os.getenv('MONGODB_ATLAS_CLUSTER_URI')


mongodb_client =  MongoClient(MONGODB_ATLAS_CLUSTER_URI)
db = mongodb_client["test"]


    
app = FastAPI()

class User(BaseModel):
    name: str
    email: str
    password:str
def parse_json(data):
    return json.loads(json_util.dumps(data))

@app.post("/users", response_description="Create a new book", status_code=status.HTTP_201_CREATED)
def create_book( book: User = Body(...)):
    book = jsonable_encoder(book)
    new_book = db["users"].insert_one(book)
    
    id = db["users"].insert_one(book).inserted_id

    new_book["_id"] = f'{id}'

    created_book = db["users"].find_one(
        {"_id": id}
    )

    return created_book



# @app.get("/users/{id}", response_description="Get a single book by id", response_model=User)
# def find_book(id: str):
#     user = db["users"].find_one({"_id": id})
#     if (user) is not None:
#         return user







if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)