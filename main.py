from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import tempfile
from utils import process_pdf
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/test")
async def test_endpoint():
    """
    Simple testing endpoint to verify the service is up.
    Returns a JSON payload with a status message.
    """
    return JSONResponse(content={"status": "ok", "message": "Testing endpoint works!"})

@app.post("/process")
async def process_pdf_endpoint(file: UploadFile = File(...)):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_pdf_path = os.path.join(temp_dir, file.filename)
        
        try:
            with open(temp_pdf_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Could not save file: {str(e)}")
            
        try:
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.0-pro-preview")
            result_text = process_pdf(temp_pdf_path, model=model_name)
            return JSONResponse(content={"text": result_text})
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
