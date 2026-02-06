from pydantic import BaseModel
from typing import Optional, List
from ..models.student import Student

class StudentResponse(BaseModel):
    id: str
    class_name: Optional[str]
    name: Optional[str]
    father_name: Optional[str]
    mother_name: Optional[str]
    address: Optional[str]
    mobile: Optional[str]
    alternate_mobile: Optional[str]
    college_name: Optional[str]

class StudentListResponse(BaseModel):
    students: List[StudentResponse]
    total: int
    page: int
    limit: int
