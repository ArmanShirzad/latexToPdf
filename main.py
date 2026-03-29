import tempfile
import subprocess
import os
from fastapi import FastAPI, UploadFile, File, Response, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="LaTeX to PDF API")

from typing import List, Optional

@app.post("/compile")
async def compile_latex(file: UploadFile = File(...), assets: Optional[List[UploadFile]] = File(None)):
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
                asset_path = os.path.join(temp_dir, asset.filename)
                asset_content = await asset.read()
                with open(asset_path, "wb") as af:
                    af.write(asset_content)
        
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
