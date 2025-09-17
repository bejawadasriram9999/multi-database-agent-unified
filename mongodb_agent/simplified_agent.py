"""
Simplified Multi-Database Agent using Unified MCP Server
This version uses a single MCP server for all databases, eliminating the need for a separate router.
"""

import os
import logging
from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from google.adk.tools.mcp_tool.mcp_session_manager import StdioServerParameters
from dotenv import load_dotenv

ROOT = os.path.dirname(os.path.dirname(__file__))
load_dotenv(dotenv_path=os.path.join(ROOT, ".env"))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimplifiedMultiDatabaseAgent:
    """
    Simplified multi-database agent using a single unified MCP server.
    This eliminates the need for separate MCP servers and a database router.
    """
    
    def __init__(self):
        self.unified_toolset = None
        self.agent = None
        self._initialize_unified_connection()
        self._create_agent()
    
    def _initialize_unified_connection(self):
        """Initialize the unified MCP connection."""
        logger.info("Initializing unified MCP connection...")
        
        try:
            # Use the unified MCP server that handles all databases
            self.unified_toolset = MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='python',
                        args=[os.path.join(ROOT, "mcp_servers", "unified_mcp_server.py")],
                        env={
                            "MDB_MCP_CONNECTION_STRING": os.environ.get("MDB_MCP_CONNECTION_STRING", ""),
                            "ORACLE_MCP_CONNECTION_STRING": os.environ.get("ORACLE_MCP_CONNECTION_STRING", "")
                        }
                    ),
                    timeout=60.0
                ),
            )
            logger.info("✅ Unified MCP Toolset initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize unified MCP Toolset: {e}")
            self.unified_toolset = None
    
    def _create_agent(self):
        """Create the simplified multi-database agent."""
        from .prompt import SIMPLIFIED_INSTRUCTION
        
        if not self.unified_toolset:
            raise RuntimeError("Unified MCP connection not available. Please check your database connections.")
        
        self.agent = LlmAgent(
            model='gemini-2.0-flash',
            name='simplified_multi_database_agent',
            instruction=SIMPLIFIED_INSTRUCTION,
            tools=[self.unified_toolset],
        )
        
        logger.info("✅ Simplified multi-database agent created successfully")
    
    def get_agent(self) -> LlmAgent:
        """Get the configured agent instance."""
        return self.agent
    
    def get_available_databases(self) -> list:
        """Get list of available database connections."""
        databases = []
        if os.environ.get("MDB_MCP_CONNECTION_STRING"):
            databases.extend(["MongoDB (Database A)", "MongoDB (Database B)"])
        if os.environ.get("ORACLE_MCP_CONNECTION_STRING"):
            databases.append("Oracle (Database C)")
        return databases

# Initialize the simplified multi-database agent
try:
    simplified_multi_db_agent = SimplifiedMultiDatabaseAgent()
    simplified_root_agent = simplified_multi_db_agent.get_agent()
    logger.info("✅ Simplified multi-database agent system initialized successfully")
except Exception as e:
    logger.error(f"❌ Failed to initialize simplified multi-database agent: {e}")
    raise
