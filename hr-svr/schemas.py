# schemas.py 에 추가 (이미 있으면 패스)

from pydantic import BaseModel
from typing import List

class LeaveItem(BaseModel):
    id: int
    name: str
    total_days: float
    used_days: float
    remaining_days: float

class LeaveStatusResponse(BaseModel):
    total_used_all: float
    leaves: List[LeaveItem]