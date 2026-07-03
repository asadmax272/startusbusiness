from fastapi import APIRouter, Depends, HTTPException, UploadFile
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.document import Document
from app.models.order import Order
from app.models.user import User
from app.schemas.workflow import DocumentOut
from app.services import storage

router = APIRouter(prefix="/api/documents", tags=["documents"])

ALLOWED_TYPES = {
    "passport", "address_proof", "business_info", "llc_certificate",
    "operating_agreement", "ein_letter", "seller_permit", "resale_certificate", "other",
}


def _order_belongs_to_user(order_id: str, user: User, db: Session) -> Order:
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(404, "Order not found.")
    if user.role == "client" and str(order.user_id) != str(user.id):
        raise HTTPException(403, "This order doesn't belong to you.")
    return order


@router.post("/{order_id}/upload", response_model=DocumentOut)
async def upload_document(
    order_id: str,
    doc_type: str,
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if doc_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unknown document type. Allowed: {sorted(ALLOWED_TYPES)}")
    _order_belongs_to_user(order_id, current_user, db)

    content = await file.read()
    if len(content) > 20 * 1024 * 1024:
        raise HTTPException(400, "File too large (max 20MB).")

    key = storage.build_key(order_id, file.filename or "upload")
    storage.save_file(key, content)

    doc = Document(
        order_id=order_id,
        uploaded_by=current_user.id,
        type=doc_type,
        storage_key=key,
        file_name=file.filename or "upload",
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("/order/{order_id}", response_model=list[DocumentOut])
def list_documents(order_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    _order_belongs_to_user(order_id, current_user, db)
    return db.query(Document).filter(Document.order_id == order_id).order_by(Document.created_at.desc()).all()


@router.get("/{document_id}/download")
def download_document(document_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == document_id).first()
    if not doc:
        raise HTTPException(404, "Document not found.")
    _order_belongs_to_user(str(doc.order_id), current_user, db)

    try:
        content = storage.read_file(doc.storage_key)
    except FileNotFoundError:
        raise HTTPException(404, "File is missing from storage.")

    return Response(
        content=content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{doc.file_name}"'},
    )
