from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pymongo import MongoClient
from pydantic import BaseModel
from bson import ObjectId
from dotenv import load_dotenv
import os

load_dotenv()

app = FastAPI()

# CORS cho phép frontend gọi API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kết nối MongoDB
client = MongoClient(os.getenv("DB_URL"))
db = client["tododb"]
collection = db["todos"]

# Model
class Todo(BaseModel):
    title: str
    done: bool = False

# ✅ /health — bắt buộc theo đề
@app.get("/health")
def health():
    return {"status": "ok"}

# ✅ /about — thông tin sinh viên (API version)
@app.get("/about")
def about():
    return {
        "name": "Võ Huy Nghĩa",     
        "student_id": "2251220237",   
        "class": "22CT1",            
        "app": os.getenv("APP_NAME")
    }

# ✅ GET — lấy danh sách todos
@app.get("/todos")
def get_todos():
    todos = []
    for t in collection.find():
        t["id"] = str(t["_id"])
        del t["_id"]
        todos.append(t)
    return todos

# ✅ POST — tạo todo mới
@app.post("/todos")
def create_todo(todo: Todo):
    result = collection.insert_one(todo.dict())
    return {"id": str(result.inserted_id), "message": "Created"}

# ✅ PUT — cập nhật trạng thái done
@app.put("/todos/{todo_id}")
def update_todo(todo_id: str, todo: Todo):
    result = collection.update_one(
        {"_id": ObjectId(todo_id)},
        {"$set": todo.dict()}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Not found")
    return {"message": "Updated"}

# ✅ DELETE — xóa todo
@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: str):
    collection.delete_one({"_id": ObjectId(todo_id)})
    return {"message": "Deleted"}