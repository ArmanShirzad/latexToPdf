import tempfile
import subprocess
import os
import logging
from typing import List
from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LaTeX to PDF API")

# Security: CORS Configuration
# Extract allowed origins from environment variable (comma-separated)
# Example: ALLOWED_ORIGINS="http://localhost:3000,http://192.168.1.1"
origins_str = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [origin.strip() for origin in origins_str.split(",")]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/compile")
async def compile_latex(
    file: UploadFile = File(..., description="The main .tex file"),
    assets: List[UploadFile] = File(default=[])
):
    if not file.filename.endswith(".tex"):
        raise HTTPException(status_code=400, detail="Uploaded file must be a .tex file")
    
    # Read the main content
    content = await file.read()
    
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as temp_dir:
        # Save the uploaded file to the temp directory
        tex_path = os.path.join(temp_dir, "main.tex")
        with open(tex_path, "wb") as f:
            f.write(content)
            
        # Save any additional assets to the temp directory
        if assets:
            for asset in assets:
                print(f"[DEBUG] Received asset filename: '{asset.filename}'", flush=True)
                asset_path = os.path.join(temp_dir, asset.filename)
                print(f"[DEBUG] Saving asset to: '{asset_path}'", flush=True)
                asset_content = await asset.read()
                with open(asset_path, "wb") as af:
                    af.write(asset_content)
                print(f"[DEBUG] Files in temp_dir: {os.listdir(temp_dir)}", flush=True)
        
        # Run pdflatex
        try:
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "-output-directory=.", "main.tex"],
                cwd=temp_dir,
                capture_output=True,
                text=True,
                timeout=15
            )
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=408, detail="LaTeX compilation timed out")
        
        pdf_path = os.path.join(temp_dir, "main.pdf")
        log_path = os.path.join(temp_dir, "main.log")
        
        if result.returncode != 0:
            error_message = result.stdout + "\n" + result.stderr
            if os.path.exists(log_path):
                with open(log_path, "r", encoding="utf-8", errors="replace") as log_file:
                    error_message += "\n\nLaTeX Log:\n" + log_file.read()
            return JSONResponse(status_code=400, content={"error": "Compilation failed", "details": error_message})
            
        if not os.path.exists(pdf_path):
            return JSONResponse(status_code=500, content={"error": "PDF not generated despite exit code 0"})
            
        # Read the generated PDF
        with open(pdf_path, "rb") as pdf_file:
            pdf_bytes = pdf_file.read()
            
        return Response(content=pdf_bytes, media_type="application/pdf")
