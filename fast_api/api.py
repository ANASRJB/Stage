from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
import sys
import json

# Add the parent directory (Stage) to the Python path to import LLM
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from LLM import get_bot_answer

app = FastAPI(
    title="Simple Chatbot API",
    description="Simple FastAPI backend using get_bot_answer function",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: Optional[str] = None
    messages: Optional[List[Message]] = None

class ChatResponse(BaseModel):
    response: Optional[str] = None
    answer: Optional[str] = None

current_dir = os.path.dirname(os.path.abspath(__file__))

@app.get("/")
async def root():
    return FileResponse(os.path.join(current_dir, "index.html"))

@app.get("/refresh")
async def refresh():
    """Force refresh the HTML file"""
    return FileResponse('index.html', headers={"Cache-Control": "no-cache, no-store, must-revalidate"})

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Simple Chatbot API is running"}

@app.get("/debug")
async def debug():
    """Debug endpoint to see what files exist"""
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    files = os.listdir(current_dir)
    return {"current_directory": current_dir, "files": files}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Chat endpoint using your get_bot_answer function"""
    # Extract message from either format
    if request.message:
        message = request.message
    elif request.messages and len(request.messages) > 0:
        message = request.messages[-1].content  # Get the last message content
    else:
        raise HTTPException(status_code=400, detail="No message provided")
    
    print(f"Received chat request: {message}")
    try:
        response = get_bot_answer(message)
        print(f"Generated response: {response[:50]}...")
        # Return both formats for compatibility
        return ChatResponse(response=response, answer=response)
    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.post("/api/chat", response_model=ChatResponse)
async def api_chat(request: ChatRequest):
    """Alternative chat endpoint for compatibility"""
    print(f"Received API chat request")
    return await chat(request)

@app.get("/procedures")
async def list_procedures():
    """Get list of available procedures"""
    try:
        # Go up one level to Stage, then to data/readydata
        stage_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        procedures_path = os.path.join(stage_dir, 'data', 'readydata')
        
        if os.path.exists(procedures_path):
            procedure_files = [f for f in os.listdir(procedures_path) if f.endswith('.json')]
            procedures = [f.replace('procedures_', '').replace('.json', '').replace('-', ' ').title() 
                         for f in procedure_files]
            return {"procedures": procedures}
        return {"procedures": []}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="127.0.0.1", port=8000, reload=True)
