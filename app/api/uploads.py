from fastapi import APIRouter, UploadFile, File

router = APIRouter(
    prefix="/uploads",
    tags=["uploads"]
)

@router.post("/image")
def upload_image(file: UploadFile = File(...)):
    return {"filename": file.filename}
