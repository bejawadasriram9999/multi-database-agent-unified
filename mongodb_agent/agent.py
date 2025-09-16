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

# Retrieve MongoDB connection details from environment variables
mongodb_connection_string = os.environ.get("MDB_MCP_CONNECTION_STRING")


if not mongodb_connection_string:
    logger.error("MDB_MCP_CONNECTION_STRING is not set. Please create a .env file with your MongoDB connection string.")
    logger.error("Example: MDB_MCP_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database")
    mongodb_connection_string = "mongodb+srv://test:test@localhost:27017/test"  # Fallback for testing
else:
    logger.info("MongoDB connection string found and configured")

logger.info("Initializing MongoDB MCP Toolset...")

from .prompt import INSTRUCTION

try:
    mongodb_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "mongodb-mcp-server@latest",
                ],
                env={
                    "MDB_MCP_CONNECTION_STRING": mongodb_connection_string
                }
            ),
            timeout=60.0
        ),
    )
    logger.info("MongoDB MCP Toolset initialized successfully")

    # Don't test the connection here - let it happen when needed
    # The MCP toolset will initialize the connection when first used
    logger.info("MongoDB MCP Toolset configured (connection will be established on first use)")

except Exception as e:
    logger.error(f"Failed to initialize MongoDB MCP Toolset: {e}")
    raise

# Create the MCP toolset directly (Google ADK will handle session management)
try:
    mongodb_toolset = MCPToolset(
        connection_params=StdioConnectionParams(
            server_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",
                    "mongodb-mcp-server@latest",
                ],
                env={
                    "MDB_MCP_CONNECTION_STRING": mongodb_connection_string
                }
            ),
            timeout=60.0
        ),
    )
    logger.info("MongoDB MCP Toolset initialized successfully")

except Exception as e:
    logger.error(f"Failed to initialize MongoDB MCP Toolset: {e}")
    raise

root_agent = LlmAgent(
    model='gemini-2.0-flash',
    name='mongodb_assistant_agent',
    instruction=INSTRUCTION,
    tools=[mongodb_toolset],
)

logger.info("MongoDB Assistant Agent created successfully")