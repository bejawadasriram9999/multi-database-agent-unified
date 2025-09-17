"""
FastAPI Server for Multi-Database Agent
Provides REST API endpoints for the multi-database agent system.
"""

import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Database Agent API",
    description="REST API for querying MongoDB and Oracle databases through AI agent",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Pydantic models
class QueryRequest(BaseModel):
    """Request model for database queries."""
    query: str = Field(..., description="The query to execute")
    database_preference: Optional[str] = Field(None, description="Preferred database (mongodb, oracle, auto)")
    max_results: Optional[int] = Field(1000, description="Maximum number of results to return")
    timeout: Optional[int] = Field(60, description="Query timeout in seconds")

class QueryResponse(BaseModel):
    """Response model for database queries."""
    success: bool
    result: Optional[str] = None
    database_used: Optional[str] = None
    query_type: Optional[str] = None
    execution_time: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime

class DatabaseInfo(BaseModel):
    """Model for database information."""
    name: str
    type: str
    status: str
    connection_string_configured: bool

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    timestamp: datetime
    databases: List[DatabaseInfo]
    agent_initialized: bool

# Global variables
agent_instance = None
available_databases = []

def get_agent():
    """Get or initialize the multi-database agent."""
    global agent_instance
    if agent_instance is None:
        try:
            from mongodb_agent.agent import multi_db_agent
            agent_instance = multi_db_agent
            logger.info("Multi-database agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize agent: {str(e)}"
            )
    return agent_instance

def check_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Check API key if authentication is enabled."""
    if os.getenv("API_KEY_REQUIRED", "FALSE").upper() == "TRUE":
        if not credentials or credentials.credentials != os.getenv("API_KEY"):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or missing API key"
            )
    return True

@app.on_event("startup")
async def startup_event():
    """Initialize the application on startup."""
    global available_databases
    
    logger.info("Starting Multi-Database Agent API server...")
    
    # Check database connections
    mongodb_configured = os.getenv("MDB_MCP_CONNECTION_STRING") is not None
    oracle_configured = os.getenv("ORACLE_MCP_CONNECTION_STRING") is not None
    
    available_databases = [
        DatabaseInfo(
            name="MongoDB",
            type="Document-based NoSQL",
            status="Connected" if mongodb_configured else "Not configured",
            connection_string_configured=mongodb_configured
        ),
        DatabaseInfo(
            name="Oracle",
            type="Relational SQL",
            status="Connected" if oracle_configured else "Not configured",
            connection_string_configured=oracle_configured
        )
    ]
    
    logger.info(f"Available databases: {[db.name for db in available_databases if db.connection_string_configured]}")

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Multi-Database Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        agent = get_agent()
        agent_initialized = agent is not None
    except:
        agent_initialized = False
    
    return HealthResponse(
        status="healthy" if agent_initialized else "unhealthy",
        timestamp=datetime.now(),
        databases=available_databases,
        agent_initialized=agent_initialized
    )

@app.post("/query", response_model=QueryResponse)
async def execute_query(
    request: QueryRequest,
    _: bool = Depends(check_api_key)
):
    """Execute a database query through the AI agent."""
    start_time = datetime.now()
    
    try:
        agent = get_agent()
        agent_instance = agent.get_agent()
        
        # Execute query
        result = agent_instance.run(request.query)
        
        # Determine database used
        database_used = "Unknown"
        if "mongodb" in request.query.lower() or "mongo" in request.query.lower():
            database_used = "MongoDB"
        elif "oracle" in request.query.lower() or any(sql_word in request.query.upper() for sql_word in ["SELECT", "INSERT", "UPDATE", "DELETE"]):
            database_used = "Oracle"
        
        # Determine query type
        query_type = "Read"
        query_lower = request.query.lower()
        if any(word in query_lower for word in ["insert", "add", "create"]):
            query_type = "Write"
        elif any(word in query_lower for word in ["update", "modify", "change"]):
            query_type = "Update"
        elif any(word in query_lower for word in ["delete", "remove", "drop"]):
            query_type = "Delete"
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResponse(
            success=True,
            result=result,
            database_used=database_used,
            query_type=query_type,
            execution_time=execution_time,
            timestamp=datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Query execution failed: {e}")
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return QueryResponse(
            success=False,
            error=str(e),
            execution_time=execution_time,
            timestamp=datetime.now()
        )

@app.get("/databases", response_model=List[DatabaseInfo])
async def get_databases(_: bool = Depends(check_api_key)):
    """Get information about available databases."""
    return available_databases

@app.get("/agent/info")
async def get_agent_info(_: bool = Depends(check_api_key)):
    """Get information about the AI agent."""
    try:
        agent = get_agent()
        return {
            "name": "Multi-Database Agent",
            "model": "gemini-2.0-flash",
            "available_databases": agent.get_available_databases(),
            "status": "active"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent info: {str(e)}"
        )

@app.post("/agent/chat")
async def chat_with_agent(
    request: QueryRequest,
    _: bool = Depends(check_api_key)
):
    """Chat with the AI agent (alias for /query endpoint)."""
    return await execute_query(request, _)

if __name__ == "__main__":
    # Run the server
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("DEBUG_MODE", "FALSE").upper() == "TRUE",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
