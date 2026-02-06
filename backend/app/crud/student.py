from typing import List, Optional, Dict, Any
from bson import ObjectId
from fastapi import HTTPException
from ..database import db
import pandas as pd
from io import BytesIO
from typing import Union

async def create_student(student_data: Dict[str, Any]) -> Dict:
    try:
        collection = db.get_client()[os.getenv("MONGODB_DB")]["students"]
        result = collection.insert_one(student_data)
        return {"id": str(result.inserted_id), **student_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create student: {str(e)}")

async def get_students(page: int = 1, limit: int = 10, search: Optional[str] = None) -> Dict:
    try:
        collection = db.get_client()[os.getenv("MONGODB_DB")]["students"]
        pipeline = [{"$match": {}}]
        
        if search:
            search_query = {
                "$or": [
                    {"name": {"$regex": search, "$options": "i"}},
                    {"mobile": {"$regex": search, "$options": "i"}},
                    {"college_name": {"$regex": search, "$options": "i"}}
                ]
            }
            pipeline[0]["$match"].update(search_query)
        
        pipeline.extend([
            {"$skip": (page - 1) * limit},
            {"$limit": limit},
            {"$sort": {"created_at": -1}}
        ])
        
        students = list(collection.aggregate(pipeline))
        total = collection.count_documents(pipeline[0]["$match"])
        
        return {
            "students": students,
            "total": total,
            "page": page,
            "limit": limit
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch students: {str(e)}")

async def get_student(student_id: str) -> Dict:
    try:
        collection = db.get_client()[os.getenv("MONGODB_DB")]["students"]
        student = collection.find_one({"_id": ObjectId(student_id)})
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        student["id"] = str(student["_id"])
        return student
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch student: {str(e)}")

async def update_student(student_id: str, student_data: Dict[str, Any]) -> Dict:
    try:
        collection = db.get_client()[os.getenv("MONGODB_DB")]["students"]
        result = collection.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {**student_data, "updated_at": datetime.utcnow()}}
        )
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        return await get_student(student_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update student: {str(e)}")

async def delete_student(student_id: str) -> Dict:
    try:
        collection = db.get_client()[os.getenv("MONGODB_DB")]["students"]
        result = collection.delete_one({"_id": ObjectId(student_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Student not found")
        return {"message": "Student deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete student: {str(e)}")

async def upload_excel(file_content: bytes) -> Dict:
    try:
        df = pd.read_excel(BytesIO(file_content))
        expected_columns = ["Class", "Name", "Father Name", "Mother Name", "Address", 
                          "Mobile", "Alternate Mobile", "College Name"]
        
        # Normalize column names
        df.columns = df.columns.str.strip()
        
        collection = db.get_client()[os.getenv("MONGODB_DB")]["students"]
        success_count = 0
        
        for _, row in df.iterrows():
            student_data = {}
            for col in expected_columns:
                if col in row.index and pd.notna(row[col]):
                    # Special logic: if only Class is present, treat as college name
                    if col == "Class" and all(pd.isna(row.get(c, pd.NA)) for c in expected_columns[1:]):
                        student_data["college_name"] = str(row[col])
                    else:
                        # Map Excel columns to MongoDB fields
                        field_map = {
                            "Class": "class_name",
                            "Name": "name",
                            "Father Name": "father_name",
                            "Mother Name": "mother_name",
                            "Address": "address",
                            "Mobile": "mobile",
                            "Alternate Mobile": "alternate_mobile",
                            "College Name": "college_name"
                        }
                        student_data[field_map[col]] = str(row[col])
            
            if student_data:  # Only insert if there's data
                student_data["created_at"] = datetime.utcnow()
                await create_student(student_data)
                success_count += 1
        
        return {"message": f"Successfully uploaded {success_count} students"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Excel upload failed: {str(e)}")
