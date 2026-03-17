from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

# Claims
class ClaimBase(BaseModel):
    user_name: str
    amount_claimed: float

class ClaimCreate(ClaimBase):
    pass

class ClaimResponse(ClaimBase):
    id: str
    item_id: str
    payment_file_url: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)

# Receipt Items
class ReceiptItemBase(BaseModel):
    name: str
    price: float

class ReceiptItemCreate(ReceiptItemBase):
    pass

class ReceiptItemResponse(ReceiptItemBase):
    id: str
    session_id: str
    claims: List[ClaimResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
# Summary
class UserItemSummary(BaseModel):
    item_id: str
    item_name: str
    cost: float
    payment_file_url: Optional[str] = None

class UserSummary(BaseModel):
    user_name: str
    items: List[UserItemSummary]
    total: float

class SessionSummary(BaseModel):
    session_id: str
    user_summaries: List[UserSummary]
    grand_total: float

# Sessions
class SessionBase(BaseModel):
...
    bank_account_info: Optional[str] = None

class SessionCreate(SessionBase):
    pass

class SessionResponse(SessionBase):
    id: str
    created_at: datetime
    items: List[ReceiptItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)
