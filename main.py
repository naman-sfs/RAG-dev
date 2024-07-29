from pydantic import BaseModel
from fastapi import FastAPI
from dotenv import dotenv_values
from pymongo import MongoClient
import os
import uvicorn
from bson.objectid import ObjectId
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

config = dotenv_values(".env")
MONGODB_ATLAS_CLUSTER_URI = os.getenv('MONGODB_ATLAS_CLUSTER_URI')

mongodb_client =  MongoClient(MONGODB_ATLAS_CLUSTER_URI)
db = mongodb_client["rag-mira"]

app = FastAPI()

origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://ec2-3-106-224-103.ap-southeast-2.compute.amazonaws.com:8000",
    "http://127.0.0.1:5500"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class User(BaseModel):
    name: str
    email: str
    password:str
    phone:int
    country:str

def individual_user(user):
    return {"id":str(user["_id"]),
            "name":user["name"],
            "email":user["email"]}
    
def all_users(users):
    return [individual_user(user) for user in users]
    
@app.post("/users")
def create_user( user: User ):
    new_user = db["users"].insert_one(dict(user))
    return {"success":"true","id":str(new_user.inserted_id)}

@app.get("/users")
def get_all_users():
    users = db["users"].find()
    return all_users(users)

@app.get("/users/{id}")
def find_user(id: str):
    id = ObjectId(id)
    user = db["users"].find_one({"_id":id})
    return individual_user(user)

# Conversations

class Conversation(BaseModel):
    user_id:str
    title:str
    created_at:int = int(datetime.timestamp(datetime.now()))


def single_convo(convo):
    return {"id":str(convo["_id"]),
            "title":convo["title"]}
    
def all_convo_of_user(convos):
    return [single_convo(convo) for convo in convos]

@app.post("/convo")
def create_convo( convo: Conversation ):
    convo.user_id = ObjectId(convo.user_id)
    new_convo = db["conversation"].insert_one(dict(convo))
    return {"success":"true","id":str(new_convo.inserted_id)}

@app.get("/convo/user/{id}")
def get_all_convo_of_user(id:str):
    id = ObjectId(id)
    convos = db["conversation"].find({"user_id":id})
    return all_convo_of_user(convos)

@app.get("/convo/{id}")
def find_convo(id: str):
    id = ObjectId(id)
    convo = db["conversation"].find_one({"_id":id})
    return single_convo(convo)

# Messages

class Message(BaseModel):
    conversation_id:str
    content:str
    role:str
    created_at:int = int(datetime.timestamp(datetime.now()))
    
def single_msg(msg):
    return {"id":str(msg["_id"]),
            "content":msg["content"],
            "role":msg["role"],
            "created_at":msg["created_at"]}
    
def all_msg_of_convo(msgs):
    return [single_msg(msg) for msg in msgs]

@app.post('/message')
def create_message(msg:Message):
    msg.conversation_id = ObjectId(msg.conversation_id)
    new_message = db["messages"].insert_one(dict(msg))
    return {"success":"true","id":str(new_message.inserted_id)}

@app.get('/message/convo/{id}')
def get_all_msg_of_convo(id:str):
    convo_id = ObjectId(id)
    all_messages = db["messages"].find({"conversation_id":convo_id})
    return all_msg_of_convo(all_messages)

@app.get('/message/{id}')
def get_message(id:str):
    id = ObjectId(id)
    message = db["messages"].find_one({"_id":id})
    return single_msg(message)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)