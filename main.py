from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import tempfile
from utils import process_pdf
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/test")
async def test_endpoint():
    """Endpoint de prueba."""
    return JSONResponse(content={"status": "ok", "message": "Testing endpoint works!"})

@app.post("/process")
def process_pdf_endpoint(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    return_pdf: bool = False
):
    """
    Recibe un PDF.
    - Si `return_pdf=True`: Devuelve el mismo PDF (descarga).
    - Si `return_pdf=False` (default): Procesa el PDF y devuelve JSON.
    """
    # 1. Crear archivo temporal persistente (delete=False)
    # Usamos mkstemp para tener una ruta física que FileResponse pueda leer.
    fd, temp_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)  # Cerramos el descriptor de archivo de bajo nivel

    try:
        # 2. Guardar el contenido subido
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        os.remove(temp_path)
        raise HTTPException(status_code=500, detail=f"Error saving file: {str(e)}")

    # 3. Lógica de retorno
    if return_pdf:
        # Programar borrado del archivo DESPUÉS de enviar la respuesta
        background_tasks.add_task(os.remove, temp_path)
        return FileResponse(
            path=temp_path, 
            media_type="application/pdf", 
            filename=file.filename
        )

    # 4. Procesamiento normal
    try:
        model_name = os.getenv("GEMINI_MODEL", "gemini-3.0-pro-preview")
        result_text = process_pdf(temp_path, model=model_name)
        
        # Borrar archivo temporal ahora que terminamos
        background_tasks.add_task(os.remove, temp_path)
        
        return JSONResponse(content={"text": result_text, "filename": file.filename})
    except Exception as e:
        # Asegurar borrado en caso de error
        background_tasks.add_task(os.remove, temp_path)
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
