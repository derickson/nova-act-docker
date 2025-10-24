"""FastAPI REST server for Nova Act script execution."""
import os
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import uvicorn

from runner import runner, ScriptResult


class ScriptExecutionRequest(BaseModel):
    """Request model for script execution."""
    env_vars: Optional[Dict[str, str]] = None
    args: Optional[List[str]] = None


class ScriptExecutionResponse(BaseModel):
    """Response model for script execution."""
    success: bool
    output: str
    error: Optional[str] = None
    exit_code: int = 0
    script_name: str


class ScriptListResponse(BaseModel):
    """Response model for listing scripts."""
    scripts: List[str]


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str = "1.0.0"


# Initialize FastAPI app
app = FastAPI(
    title="Nova Act Script Runner",
    description="REST API for executing Nova Act scripts in isolated environments",
    version="1.0.0"
)


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    return HealthResponse(status="healthy")


@app.get("/scripts", response_model=ScriptListResponse)
async def list_scripts():
    """List all available scripts."""
    try:
        scripts = runner.list_scripts()
        return ScriptListResponse(scripts=scripts)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list scripts: {str(e)}")


@app.post("/execute/{script_name}", response_model=ScriptExecutionResponse)
async def execute_script(
    script_name: str,
    request: ScriptExecutionRequest = ScriptExecutionRequest()
):
    """
    Execute a Nova Act script with optional environment variables and arguments.
    
    Args:
        script_name: Name of the script to execute (without .py extension)
        request: Script execution parameters
        
    Returns:
        Script execution result
    """
    # Validate script exists
    if not runner.script_exists(script_name):
        raise HTTPException(
            status_code=404, 
            detail=f"Script '{script_name}' not found"
        )
    
    # Check for required Nova Act API key
    env_vars = request.env_vars or {}
    if "NOVA_ACT_API_KEY" not in env_vars and "NOVA_ACT_API_KEY" not in os.environ:
        raise HTTPException(
            status_code=400,
            detail="NOVA_ACT_API_KEY must be provided in env_vars or as environment variable"
        )
    
    try:
        # Execute the script
        result = runner.execute_script(
            script_name=script_name,
            env_vars=env_vars,
            args=request.args
        )
        
        return ScriptExecutionResponse(
            success=result.success,
            output=result.output,
            error=result.error,
            exit_code=result.exit_code,
            script_name=script_name
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to execute script: {str(e)}"
        )


@app.get("/validate/{script_name}")
async def validate_script(script_name: str):
    """
    Validate a script's syntax without executing it.
    
    Args:
        script_name: Name of the script to validate
        
    Returns:
        Validation result
    """
    if not runner.script_exists(script_name):
        raise HTTPException(
            status_code=404,
            detail=f"Script '{script_name}' not found"
        )
    
    try:
        result = runner.validate_script(script_name)
        return {
            "valid": result.success,
            "message": result.output if result.success else result.error,
            "script_name": script_name
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to validate script: {str(e)}"
        )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Global exception handler."""
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": "internal_error"
        }
    )


if __name__ == "__main__":
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    
    # Run the server
    uvicorn.run(
        "server:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        access_log=True
    )
