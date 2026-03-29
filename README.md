# LatexToPdf API

LatexToPdf is a lightweight, containerized Python web API built with FastAPI that compiles LaTeX files into highly precise PDF documents. 

## Features

- RESTful Endpoint (`POST /compile`) to accept `.tex` and supplementary files.
- Generates and returns a `.pdf` payload securely.
- Isolated container compilation (every compilation uses its own temporary workspace).
- Integrated Docker and GHCR image publishing.
- High-performance asyncio engine.

## Usage

### Using Docker (Recommended)

You can pull the pre-built image from GHCR or build it yourself:

```bash
docker build -t latex-api .
docker run -p 8080:80 latex-api
```

### Local Development

If you prefer to run it locally without Docker:

```bash
# 1. Create and activate a Virtual Environment
python3 -m venv .venv_new
source .venv_new/bin/activate

# 2. Install Dependencies
pip install -r requirements.txt

# 3. Ensure you have a LaTeX distribution installed (e.g., MacTeX, TeX Live)

# 4. Start the Application
uvicorn main:app --port 8080
```

## API Testing

You can easily compile a document by sending a `POST` request.

Basic Compilation (Single File):
```bash
curl -X POST -F "file=@sample.tex" http://localhost:8080/compile --output output.pdf
```

Advanced Compilation (With Assets like local images):
```bash
curl -X POST -F "file=@sample.tex" -F "assets=@headshot.jpg" http://localhost:8080/compile --output output.pdf
```
