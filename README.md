# Google ADK MongoDB MCP Server

This project provides a MongoDB assistant using Google's ADK (AI Development Kit) with the MongoDB MCP (Model Context Protocol) server.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   # or with uv
   uv sync
   ```

2. **Configure MongoDB Connection:**

   Create a `.env` file in the project root with your MongoDB connection string:

   ```env
   # Get this from your MongoDB Atlas cluster connection string
   # Go to: https://cloud.mongodb.com → Clusters → Connect → Connect your application
   MDB_MCP_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database
   ```

   **Alternative: Using API Keys (if preferred):**

   ```env
   # Get these from https://cloud.mongodb.com/v2#/account/apiKeys
   MDB_MCP_API_CLIENT_ID=your_api_client_id
   MDB_MCP_API_CLIENT_SECRET=your_api_client_secret
   ```

3. **Run the agent:**
   ```bash
   python -m src.agent
   ```

## What was fixed

The implementation was updated to use the **connection string approach** which is simpler and more reliable than API keys. The MongoDB MCP server supports two authentication methods:

1. **Connection String** (recommended): Direct MongoDB connection string
2. **API Keys**: MongoDB Atlas API keys with `MDB_MCP_API_CLIENT_ID` and `MDB_MCP_API_CLIENT_SECRET`

The connection string approach is preferred as it's more straightforward and doesn't require API key setup in Atlas.
