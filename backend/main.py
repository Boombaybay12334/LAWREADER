import os
import tempfile
import subprocess
import shutil
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime
from dotenv import dotenv_values
import json
# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Legal Document Analyzer API",
    description="API for legal document analysis and query processing",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class LegalQuery(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str
    timestamp: datetime
    query_id: str

class AnalysisResponse(BaseModel):
    message: str
    file_id: str
    timestamp: datetime

# Configuration
UPLOAD_DIR = Path("uploads")
PROCESSED_DIR = Path("processed")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Ensure directories exist
UPLOAD_DIR.mkdir(exist_ok=True)
PROCESSED_DIR.mkdir(exist_ok=True)

def cleanup_old_files():
    """Clean up files older than 1 hour"""
    try:
        current_time = datetime.now()
        for directory in [UPLOAD_DIR, PROCESSED_DIR]:
            for file_path in directory.glob("*"):
                if file_path.is_file():
                    file_age = current_time - datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_age.total_seconds() > 3600:  # 1 hour
                        file_path.unlink()
    except Exception as e:
        logger.error(f"Error cleaning up files: {e}")

def validate_pdf(file: UploadFile) -> bool:
    """Validate PDF file"""
    if not file.filename.lower().endswith('.pdf'):
        return False
    return True

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.post("/upload-pdf", response_model=AnalysisResponse)
async def analyze_pdf(file: UploadFile = File(...)):
    """
    Upload and analyze PDF document using Tool 1
    """
    try:
        # Validate file
        if not validate_pdf(file):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload a PDF file.")
        
        # Check file size
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large. Maximum size is 10MB.")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        original_filename = file.filename
        input_path = UPLOAD_DIR / f"{file_id}_{original_filename}"
        output_path = PROCESSED_DIR / f"{file_id}_processed.pdf"
        
        # Save uploaded file
        with open(input_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"File uploaded: {input_path}")
        
        # Execute Tool 1 (PDF Document Analyzer)
        # For demo purposes, we'll simulate the processing
        # In reality, you would run: python -m pipeline.main --file [PDF_PATH]
        
# Execute Tool 1 (PDF Document Analyzer)
        try:
            # Get the root directory (parent of backend folder)
            root_dir = Path(__file__).parent.parent
            tool1_path = root_dir / "tool1"
            

            tool1_python = tool1_path / "venv" / "Scripts" / "python.exe"


            if not tool1_python.exists():
                raise HTTPException(status_code=500, detail="Tool1 virtual environment not found")
            


            tool1_env_path = tool1_path / ".env"
            tool1_env = dotenv_values(dotenv_path=tool1_env_path)
            env = os.environ.copy()
            env.update(tool1_env)


            # Execute your actual tool with its venv
            result = subprocess.run([
                str(tool1_python), "-m", "pipeline.main", "--file", str(input_path.absolute())
            ], cwd=str(tool1_path), capture_output=True, text=True, timeout=300,env=env)


            logger.info("RESULT: {result}")
            print("RESULT IS: ",result)
            if result.returncode != 0:
                logger.error(f"Tool1 stderr: {result.stderr}")
                raise HTTPException(status_code=500, detail=f"Processing failed: {result.stderr}")
            
            # Check if your tool creates output in a specific location
            # You might need to adjust this based on where your tool saves the processed PDF
            # For now, assuming it processes in place or creates output in same directory
            
            # If your tool creates output with a specific naming pattern, adjust accordingly
            # This is a placeholder - you may need to modify based on your tool's output behavior
            tool_output_path = tool1_path / "Legal_Analysis_Report.pdf"

            if not tool_output_path.exists():
                raise HTTPException(status_code=500, detail="Tool didn't generate Legal_Analysis_Report.pdf")

            shutil.move(str(tool_output_path), str(output_path))

            logger.info(f"File processed successfully: {output_path}")
            
            # Clean up input file
            input_path.unlink()
            
            return AnalysisResponse(
                message="PDF processed successfully",
                file_id=file_id,
                timestamp=datetime.now()
            )
            
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Processing timeout. Please try again.")
        except Exception as e:
            logger.error(f"Processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/download/{file_id}")
async def download_processed_file(file_id: str):
    """
    Download processed PDF file
    """
    try:
        file_path = PROCESSED_DIR / f"{file_id}_processed.pdf"
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            filename=f"processed_{file_id}.pdf",
            media_type="application/pdf"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Download error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/legal-query", response_model=QueryResponse)
async def process_legal_query(query: LegalQuery):
    """
    Process legal query using Tool 2
    """
    try:
        if not query.question.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty")
        
        if len(query.question) > 1000:
            raise HTTPException(status_code=400, detail="Query too long. Maximum 1000 characters.")
        
        logger.info(f"Processing query: {query.question}")
        
        # Execute Tool 2 (Legal Query System)
        # For demo purposes, we'll simulate the response
        # In reality, you would run: python lawreader_main.py -q "[QUESTION]"
        
# Execute Tool 2 (Legal Query System)
        try:
            # Get the root directory (parent of backend folder)
            root_dir = Path(__file__).parent.parent
            tool2_path = root_dir / "tool2"
            
            tool2_python = tool2_path / "venv" / "Scripts" / "python.exe"
            # Linux/Mac:
            # tool2_python = tool2_path / "venv" / "bin" / "python"
            
            # Check if venv exists
            if not tool2_python.exists():
                raise HTTPException(status_code=500, detail="Tool2 virtual environment not found")

            # Load Tool2-specific .env
            tool2_env_path = tool2_path /".env"
            tool2_env = dotenv_values(dotenv_path=tool2_env_path)


            env = os.environ.copy()
            env.update(tool2_env)

# DEBUG: Make sure vars are there
            print("✅ GRAPH_PATH:", env.get("GRAPH_PATH"))
            print("✅ LLM_API_KEY:", "Loaded" if env.get("LLM_API_KEY") else "Missing")


            # Merge with base environment
            env = os.environ.copy()
            env.update(tool2_env)


            logger.info(f"Tool2 environment before subprocess: {env}")
  


            # Execute your actual tool with its venv
            result = subprocess.run([
                str(tool2_python), "lawreader_main.py", "-q", query.question
            ], cwd=str(tool2_path), capture_output=True, text=True,encoding="utf-8",errors="ignore", timeout=600,env=env)
            

#            if result.returncode != 0:
#                logger.error(f"Tool2 stderr: {result.stderr}")
#                raise HTTPException(status_code=500, detail=f"Query processing failed: {result.stderr}")
            
            # Get the answer from your tool's output

            
            import unicodedata

            def remove_non_ascii(text):
                return unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')

            raw_output = remove_non_ascii(result.stdout.strip())
            logger.info(f"See answer:{raw_output}")
            def extract_final_answer(text: str) -> str:
                marker = "ANSWER:"
                idx = text.find(marker)
                return text[idx:].strip() if idx != -1 else "No valid answer found in output."

            answer = extract_final_answer(raw_output)
            logger.info(f"See answer:{answer}")

            
            # If your tool doesn't return anything in stdout, check stderr or adjust accordingly
            if not answer:
                answer = "No response received from the legal query system. Please try again."          
            query_id = str(uuid.uuid4())
            
            logger.info(f"Query processed successfully: {query_id}")
            
            print("✅ About to return this JSON response:", {
            "answer": answer,
            "timestamp": datetime.now(),
            "query_id": query_id
            })


            return QueryResponse(
                answer=answer,
                timestamp=datetime.now(),
                query_id=query_id
            )
            
        except subprocess.TimeoutExpired:
            raise HTTPException(status_code=500, detail="Query processing timeout. Please try again.")
        except Exception as e:
            logger.error(f"Query processing error: {e}")
            raise HTTPException(status_code=500, detail=f"Query processing failed: {str(e)}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Query error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.on_event("startup")
async def startup_event():
    """Startup event handler"""
    cleanup_old_files()
    logger.info("Legal Document Analyzer API started")

@app.on_event("shutdown")
async def shutdown_event():
    """Shutdown event handler"""
    logger.info("Legal Document Analyzer API shutting down")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)