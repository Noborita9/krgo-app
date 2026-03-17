import os
import uuid
import vercel_blob
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from api.database import get_db
from api.models import Session, ReceiptItem, Claim
from api.schemas import (
    SessionCreate, 
    SessionResponse, 
    ClaimCreate, 
    ClaimResponse, 
    ReceiptItemResponse,
    SessionSummary,
    UserSummary
)
from api.services.receipt_parser import parse_receipt_image

router = APIRouter(prefix="/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse)
async def create_session(session_data: SessionCreate, db: AsyncSession = Depends(get_db)):
    new_session = Session(bank_account_info=session_data.bank_account_info)
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)
    # The newly created session has empty items, returning it via schema is fine
    return new_session

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str, db: AsyncSession = Depends(get_db)):
    # Load session with its items and their claims
    stmt = (
        select(Session)
        .options(selectinload(Session.items).selectinload(ReceiptItem.claims))
        .where(Session.id == session_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    return session

@router.post("/{session_id}/receipt", response_model=list[ReceiptItemResponse])
async def upload_receipt(
    session_id: str, 
    file: UploadFile = File(...), 
    db: AsyncSession = Depends(get_db)
):
    # Verify session exists
    stmt = select(Session).where(Session.id == session_id)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Parse the image using our service
    parsed_items = await parse_receipt_image(file)
    
    # Save the parsed items into the database
    created_items = []
    for item_dict in parsed_items:
        for name, price in item_dict.items():
            new_item = ReceiptItem(session_id=session_id, name=name, price=price)
            db.add(new_item)
            created_items.append(new_item)
            
    await db.commit()
    
    # Refresh to get IDs
    for item in created_items:
        await db.refresh(item)
        
    return created_items

@router.post("/{session_id}/items/{item_id}/claim", response_model=ClaimResponse)
async def claim_item(
    session_id: str, 
    item_id: str, 
    claim_data: ClaimCreate, 
    db: AsyncSession = Depends(get_db)
):
    # Verify item exists and belongs to the session
    stmt = select(ReceiptItem).where(ReceiptItem.id == item_id, ReceiptItem.session_id == session_id)
    result = await db.execute(stmt)
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(status_code=404, detail="Receipt item not found in this session")

    # Create the claim
    new_claim = Claim(
        item_id=item_id,
        user_name=claim_data.user_name,
        amount_claimed=claim_data.amount_claimed
    )
    db.add(new_claim)
    await db.commit()
    await db.refresh(new_claim)
    
    return new_claim

@router.post("/{session_id}/items/{item_id}/pay", response_model=ClaimResponse)
async def upload_payment_confirmation(
    session_id: str,
    item_id: str,
    user_name: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Find the claim for this user and item
    stmt = (
        select(Claim)
        .join(ReceiptItem)
        .where(
            ReceiptItem.id == item_id,
            ReceiptItem.session_id == session_id,
            Claim.user_name == user_name
        )
    )
    result = await db.execute(stmt)
    claim = result.scalar_one_or_none()

    if not claim:
        raise HTTPException(status_code=404, detail="Claim not found for this user and item")

    # Upload to Vercel Blob
    content = await file.read()
    file_extension = os.path.splitext(file.filename)[1]
    blob_name = f"payments/{uuid.uuid4()}{file_extension}"
    
    try:
        # put() returns an object with a 'url' attribute
        blob = vercel_blob.put(blob_name, content)
        # We'll use the column 'payment_file_path' to store the URL
        claim.payment_file_path = blob.url
    except Exception as e:
        print(f"Vercel Blob upload failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload file to storage")

    await db.commit()
    await db.refresh(claim)

    return claim

@router.get("/{session_id}/summary", response_model=SessionSummary)
async def get_session_summary(session_id: str, db: AsyncSession = Depends(get_db)):
    # Load session with its items and their claims
    stmt = (
        select(Session)
        .options(selectinload(Session.items).selectinload(ReceiptItem.claims))
        .where(Session.id == session_id)
    )
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    user_data = {} # {user_name: {"items": [], "total": 0.0}}
    grand_total = 0.0

    for item in session.items:
        for claim in item.claims:
            user_name = claim.user_name
            if user_name not in user_data:
                user_data[user_name] = {"items": [], "total": 0.0}
            
            # Cost is based on the fraction claimed of the item's price
            # e.g. if user claims 0.5 of a $10 item, cost is $5
            cost = claim.amount_claimed * item.price
            
            user_data[user_name]["items"].append({
                "item_id": item.id,
                "item_name": item.name,
                "cost": cost,
                "payment_file_url": claim.payment_file_path
            })
            user_data[user_name]["total"] += cost
            grand_total += cost

    user_summaries = [
        UserSummary(
            user_name=name,
            items=data["items"],
            total=data["total"]
        ) for name, data in user_data.items()
    ]

    return SessionSummary(
        session_id=session_id,
        user_summaries=user_summaries,
        grand_total=grand_total
    )
