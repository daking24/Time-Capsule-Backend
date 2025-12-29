import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, UploadFile, File, HTTPException
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Configure Cloudinary
cloudinary.config( 
  cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.getenv("CLOUDINARY_API_KEY"), 
  api_secret = os.getenv("CLOUDINARY_API_SECRET"),
  secure = True
)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Upload the file to Cloudinary
        # We can detect the resource type automatically (image, video, raw)
        result = cloudinary.uploader.upload(file.file, resource_type="auto")
        
        return {
            "url": result.get("secure_url"),
            "public_id": result.get("public_id"),
            "resource_type": result.get("resource_type")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
