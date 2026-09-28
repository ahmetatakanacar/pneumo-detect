import uuid
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session
from api.deps import get_current_user, require_role
from db.database import get_db
from db.models import AnalysisResult, User, UserRole
from schemas.xray import AnalysisResultOut
from services.prediction import predict

router = APIRouter(tags=["xray"])

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png"}

@router.post("/upload-xray", response_model=AnalysisResultOut, status_code=status.HTTP_201_CREATED)
def upload_xray(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.DOCTOR, UserRole.ADMIN)),
):
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(status_code=400, detail="Sadece JPEG/PNG görüntüler kabul edilir")

    image_bytes = file.file.read()
    prediction = predict(image_bytes)

    result = AnalysisResult(
        user_id=current_user.id,
        result=prediction["result"],
        confidence=prediction["confidence"],
    )
    db.add(result)
    db.commit()
    db.refresh(result)
    return result

@router.get("/get-result/{result_id}", response_model=AnalysisResultOut)
def get_result(
    result_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()
    if result is None:
        raise HTTPException(status_code=404, detail="Sonuç bulunamadı")
    return result