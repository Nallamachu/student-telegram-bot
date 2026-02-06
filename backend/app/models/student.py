from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StudentBase(BaseModel):
    class_name: Optional[str] = None
    name: Optional[str] = None
    father_name: Optional[str] = None
    mother_name: Optional[str] = None
    address: Optional[str] = None
    mobile: Optional[str] = None
    alternate_mobile: Optional[str] = None
    college_name: Optional[str] = None

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class Student(StudentBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True
