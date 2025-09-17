import os
import logging
from typing import List, Optional
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

class MultiDatabaseAgent:
    """
    Production-ready multi-database agent supporting MongoDB and Oracle databases
    via MCP (Model Context Protocol) servers.
    """
    
    def __init__(self):
        self.mongodb_toolset = None
        self.oracle_toolset = None
        self.agent = None
        self._initialize_connections()
        self._create_agent()
    
    def _initialize_connections(self):
        """Initialize MCP connections for both MongoDB and Oracle databases."""
        logger.info("Initializing multi-database MCP connections...")
        
        # Initialize MongoDB connection
        self._init_mongodb_connection()
        
        # Initialize Oracle connection
        self._init_oracle_connection()
    
    def _init_mongodb_connection(self):
        """Initialize MongoDB MCP connection."""
        mongodb_connection_string = os.environ.get("MDB_MCP_CONNECTION_STRING")
        
        if not mongodb_connection_string:
            logger.warning("MDB_MCP_CONNECTION_STRING not set. MongoDB functionality will be disabled.")
            return
        
        try:
            # Use our custom MongoDB MCP server
            self.mongodb_toolset = MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='python',
                        args=[os.path.join(ROOT, "mcp_servers", "mongodb_mcp_server.py")],
                        env={"MDB_MCP_CONNECTION_STRING": mongodb_connection_string}
                    ),
                    timeout=60.0
                ),
            )
            logger.info("MongoDB MCP Toolset initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB MCP Toolset: {e}")
            self.mongodb_toolset = None
    
    def _init_oracle_connection(self):
        """Initialize Oracle MCP connection."""
        oracle_connection_string = os.environ.get("ORACLE_MCP_CONNECTION_STRING")
        
        if not oracle_connection_string:
            logger.warning("ORACLE_MCP_CONNECTION_STRING not set. Oracle functionality will be disabled.")
            return
        
        try:
            # For Oracle, we'll use a custom MCP server implementation
            # This assumes you have an Oracle MCP server running
            self.oracle_toolset = MCPToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='python',
                        args=[os.path.join(ROOT, "mcp_servers", "oracle_mcp_server.py")],
                        env={"ORACLE_CONNECTION_STRING": oracle_connection_string}
                    ),
                    timeout=60.0
                ),
            )
            logger.info("Oracle MCP Toolset initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Oracle MCP Toolset: {e}")
            self.oracle_toolset = None
    
    def _create_agent(self):
        """Create the multi-database agent with available toolsets."""
        from .prompt import INSTRUCTION
        
        # Collect available toolsets
        toolsets = []
        if self.mongodb_toolset:
            toolsets.append(self.mongodb_toolset)
        if self.oracle_toolset:
            toolsets.append(self.oracle_toolset)
        
        if not toolsets:
            raise RuntimeError("No database connections available. Please configure at least one database connection.")
        
        self.agent = LlmAgent(
            model='gemini-2.0-flash',
            name='multi_database_agent',
            instruction=INSTRUCTION,
            tools=toolsets,
        )
        
        logger.info(f"Multi-database agent created successfully with {len(toolsets)} database connection(s)")
    
    def get_agent(self) -> LlmAgent:
        """Get the configured agent instance."""
        return self.agent
    
    def get_available_databases(self) -> List[str]:
        """Get list of available database connections."""
        databases = []
        if self.mongodb_toolset:
            databases.append("MongoDB")
        if self.oracle_toolset:
            databases.append("Oracle")
        return databases

# Initialize the multi-database agent
try:
    multi_db_agent = MultiDatabaseAgent()
    root_agent = multi_db_agent.get_agent()
    logger.info("Multi-database agent system initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize multi-database agent: {e}")
    raise