from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
import os
from dotenv import load_dotenv
from .database import db
from .config_manager import init_app_config
from .crud.student import (
    get_students, get_student, create_student, update_student, 
    delete_student, upload_excel
)
from .crud.user import (
    create_user, authenticate_user, get_users, get_user, 
    update_user, delete_user, forgot_password
)
from .auth.jwt import create_access_token
from .schemas.student import StudentListResponse, StudentResponse
from .schemas.user import UserCreate, UserUpdate, Token
from .dependencies import get_current_user
from .models.user import User
from .telegram.sender import send_bulk_telegram_messages
import pandas as pd
from typing import List

load_dotenv()

app = FastAPI(title="Student Management System", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create default admin on startup
@app.on_event("startup")
async def startup_event():
    # Initialize application configuration in `app_config` collection
    defaults = {
        "SECRET_KEY": os.getenv("SECRET_KEY", ""),
        "TELEGRAM_BOT_TOKEN": os.getenv("TELEGRAM_BOT_TOKEN", ""),
        "ALGORITHM": os.getenv("ALGORITHM", "HS256"),
        "ACCESS_TOKEN_EXPIRE_MINUTES": os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    }
    init_app_config(defaults)

    collection = db.get_client()[os.getenv("MONGODB_DB")]["users"]
    if collection.count_documents({"username": "admin"}) == 0:
        await create_user({
            "username": "admin",
            "password": "admin@123",
            "is_admin": True
        })

# Auth Endpoints
@app.post("/api/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/forgot-password")
async def forgot_password_endpoint(email: str):
    result = await forgot_password(email)
    return result

# User CRUD (Admin only)
@app.get("/api/users", response_model=List[User])
async def read_users(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin only")
    return await get_users()

# Student CRUD
@app.post("/api/students", response_model=StudentResponse)
async def create_new_student(
    student_data: dict,
    current_user: User = Depends(get_current_user)
):
    return await create_student(student_data)

@app.get("/api/students", response_model=StudentListResponse)
async def read_students(
    page: int = 1,
    limit: int = 10,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    result = await get_students(page, limit, search)
    return StudentListResponse(**result)

@app.get("/api/students/{student_id}", response_model=StudentResponse)
async def read_student(student_id: str, current_user: User = Depends(get_current_user)):
    return await get_student(student_id)

@app.put("/api/students/{student_id}", response_model=StudentResponse)
async def update_existing_student(
    student_id: str,
    student_data: dict,
    current_user: User = Depends(get_current_user)
):
    return await update_student(student_id, student_data)

@app.delete("/api/students/{student_id}")
async def delete_existing_student(
    student_id: str,
    current_user: User = Depends(get_current_user)
):
    return await delete_student(student_id)

@app.post("/api/students/upload")
async def upload_students_file(file: UploadFile = File(...)):
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Only Excel files allowed")
    contents = await file.read()
    return await upload_excel(contents)

@app.post("/api/telegram/bulk-send")
async def bulk_send_telegram(
    mobiles: List[str],
    message: str,
    image_url: Optional[str] = None,
    video_url: Optional[str] = None,
    current_user: User = Depends(get_current_user)
):
    result = await send_bulk_telegram_messages(mobiles, message, image_url, video_url)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
