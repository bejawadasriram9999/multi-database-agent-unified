#!/usr/bin/env python3
"""
Unified MCP Server for Multi-Database Agent
Handles MongoDB and Oracle databases in a single MCP server with built-in routing.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union
import pymongo
from pymongo import MongoClient
from bson import ObjectId, json_util
import oracledb
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    ListToolsRequest,
    ListToolsResult,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedMCPServer:
    """
    Unified MCP Server that handles both MongoDB and Oracle databases
    with built-in intelligent routing.
    """
    
    def __init__(self):
        self.server = Server("unified-multi-database-server")
        self.mongodb_client = None
        self.oracle_connection = None
        self._setup_handlers()
        self._connect_to_databases()
    
    def _connect_to_databases(self):
        """Establish connections to both MongoDB and Oracle databases."""
        # Connect to MongoDB
        mongodb_connection_string = os.environ.get("MDB_MCP_CONNECTION_STRING")
        if mongodb_connection_string:
            try:
                self.mongodb_client = MongoClient(mongodb_connection_string, serverSelectionTimeoutMS=5000)
                self.mongodb_client.admin.command('ping')
                logger.info("✅ Connected to MongoDB")
            except Exception as e:
                logger.error(f"❌ Failed to connect to MongoDB: {e}")
                self.mongodb_client = None
        
        # Connect to Oracle
        oracle_connection_string = os.environ.get("ORACLE_MCP_CONNECTION_STRING")
        if oracle_connection_string:
            try:
                self.oracle_connection = oracledb.connect(oracle_connection_string)
                logger.info("✅ Connected to Oracle")
            except Exception as e:
                logger.error(f"❌ Failed to connect to Oracle: {e}")
                self.oracle_connection = None
    
    def _determine_database_type(self, query: str, explicit_db: str = None) -> str:
        """
        Determine which database to use based on query analysis.
        This replaces the separate database router.
        """
        query_lower = query.lower()
        
        # Check for explicit database specification
        if explicit_db:
            if explicit_db.lower() in ['mongodb', 'mongo', 'database a', 'database b', 'db a', 'db b']:
                return 'mongodb'
            elif explicit_db.lower() in ['oracle', 'database c', 'db c']:
                return 'oracle'
        
        # Check for explicit database mentions in query
        if any(db in query_lower for db in ['database a', 'database b', 'db a', 'db b', 'mongodb', 'mongo']):
            return 'mongodb'
        elif any(db in query_lower for db in ['database c', 'db c', 'oracle']):
            return 'oracle'
        
        # Check for MongoDB patterns
        mongodb_patterns = [
            r'db\.\w+\.',
            r'\.find\(',
            r'\.aggregate\(',
            r'\.insertOne\(',
            r'\.updateOne\(',
            r'\.deleteOne\(',
            r'\$match',
            r'\$group',
            r'\$lookup',
            r'\$project',
            r'collection',
            r'document'
        ]
        
        for pattern in mongodb_patterns:
            if pattern in query_lower:
                return 'mongodb'
        
        # Check for SQL patterns
        sql_patterns = [
            r'\bselect\b',
            r'\binsert\b',
            r'\bupdate\b',
            r'\bdelete\b',
            r'\bcreate\b',
            r'\balter\b',
            r'\bdrop\b',
            r'\btable\b',
            r'\bfrom\b',
            r'\bwhere\b',
            r'\bgroup by\b',
            r'\border by\b'
        ]
        
        for pattern in sql_patterns:
            if pattern in query_lower:
                return 'oracle'
        
        # Check for keywords
        mongodb_keywords = ['users', 'products', 'orders', 'analytics', 'collections', 'documents']
        oracle_keywords = ['employees', 'departments', 'projects', 'sales', 'tables', 'schemas']
        
        mongodb_score = sum(1 for keyword in mongodb_keywords if keyword in query_lower)
        oracle_score = sum(1 for keyword in oracle_keywords if keyword in query_lower)
        
        if mongodb_score > oracle_score:
            return 'mongodb'
        elif oracle_score > mongodb_score:
            return 'oracle'
        
        # Default to unknown if ambiguous
        return 'unknown'
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available tools for both databases."""
            return ListToolsResult(
                tools=[
                    # Universal tools
                    Tool(
                        name="query_database",
                        description="Execute a query on any database (MongoDB or Oracle) with automatic routing",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "The query to execute (natural language or SQL/MongoDB syntax)"
                                },
                                "database": {
                                    "type": "string",
                                    "description": "Optional: specify database (mongodb, oracle, database a/b/c)"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of results to return",
                                    "default": 100
                                }
                            },
                            "required": ["query"]
                        }
                    ),
                    Tool(
                        name="list_databases",
                        description="List all available databases and their status",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="get_database_info",
                        description="Get detailed information about a specific database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name (mongodb, oracle, database a/b/c)"
                                }
                            },
                            "required": ["database"]
                        }
                    ),
                    # MongoDB-specific tools
                    Tool(
                        name="mongodb_find",
                        description="Find documents in MongoDB collections",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "MongoDB database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "query": {
                                    "type": "object",
                                    "description": "MongoDB query filter"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of documents",
                                    "default": 10
                                }
                            },
                            "required": ["database", "collection"]
                        }
                    ),
                    Tool(
                        name="mongodb_aggregate",
                        description="Run aggregation pipeline on MongoDB collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "MongoDB database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "pipeline": {
                                    "type": "array",
                                    "description": "Aggregation pipeline stages"
                                }
                            },
                            "required": ["database", "collection", "pipeline"]
                        }
                    ),
                    # Oracle-specific tools
                    Tool(
                        name="oracle_execute_sql",
                        description="Execute SQL query on Oracle database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "sql": {
                                    "type": "string",
                                    "description": "SQL query to execute"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of rows",
                                    "default": 100
                                }
                            },
                            "required": ["sql"]
                        }
                    ),
                    Tool(
                        name="oracle_list_tables",
                        description="List all tables in Oracle database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "schema": {
                                    "type": "string",
                                    "description": "Schema name (optional)"
                                }
                            }
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls with built-in routing."""
            try:
                if name == "query_database":
                    return await self._handle_universal_query(arguments)
                elif name == "list_databases":
                    return await self._list_databases()
                elif name == "get_database_info":
                    return await self._get_database_info(arguments)
                elif name == "mongodb_find":
                    return await self._mongodb_find(arguments)
                elif name == "mongodb_aggregate":
                    return await self._mongodb_aggregate(arguments)
                elif name == "oracle_execute_sql":
                    return await self._oracle_execute_sql(arguments)
                elif name == "oracle_list_tables":
                    return await self._oracle_list_tables(arguments)
                else:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Unknown tool: {name}"
                        )]
                    )
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text=f"Error executing {name}: {str(e)}"
                    )]
                )
    
    async def _handle_universal_query(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Handle universal queries with automatic database routing."""
        query = arguments.get("query", "")
        explicit_db = arguments.get("database")
        limit = arguments.get("limit", 100)
        
        if not query:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: No query provided"
                )]
            )
        
        # Determine which database to use
        db_type = self._determine_database_type(query, explicit_db)
        
        if db_type == 'unknown':
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="I'm not sure which database to query. Please specify:\n" +
                         "- 'MongoDB' or 'Database A/B' for document queries\n" +
                         "- 'Oracle' or 'Database C' for SQL queries\n" +
                         f"Your query: {query}"
                )]
            )
        
        # Route to appropriate database
        if db_type == 'mongodb':
            return await self._route_to_mongodb(query, limit)
        elif db_type == 'oracle':
            return await self._route_to_oracle(query, limit)
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text=f"Unable to process query: {query}"
            )]
        )
    
    async def _route_to_mongodb(self, query: str, limit: int) -> CallToolResult:
        """Route query to MongoDB."""
        if not self.mongodb_client:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="MongoDB connection not available"
                )]
            )
        
        try:
            # Simple query routing for MongoDB
            if "list databases" in query.lower():
                db_list = self.mongodb_client.list_database_names()
                result = f"MongoDB Databases ({len(db_list)}):\n" + "\n".join(f"- {db}" for db in db_list)
            elif "list collections" in query.lower():
                # Extract database name from query or use default
                db_name = "test_company_db"  # Default for demo
                db = self.mongodb_client[db_name]
                collections = db.list_collection_names()
                result = f"Collections in {db_name} ({len(collections)}):\n" + "\n".join(f"- {col}" for col in collections)
            elif "find" in query.lower() and "users" in query.lower():
                # Simple user query
                db = self.mongodb_client["test_company_db"]
                collection = db["users"]
                if "active" in query.lower():
                    docs = list(collection.find({"status": "active"}).limit(limit))
                else:
                    docs = list(collection.find().limit(limit))
                result = f"Found {len(docs)} users:\n" + json.dumps(docs, indent=2, default=json_util.default)
            else:
                result = f"MongoDB query processed: {query}\n(Implementation would handle specific query patterns)"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"🔵 MongoDB Query Result:\n{result}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"MongoDB query failed: {str(e)}"
                )]
            )
    
    async def _route_to_oracle(self, query: str, limit: int) -> CallToolResult:
        """Route query to Oracle."""
        if not self.oracle_connection:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Oracle connection not available"
                )]
            )
        
        try:
            cursor = self.oracle_connection.cursor()
            
            # Simple query routing for Oracle
            if "list tables" in query.lower():
                cursor.execute("SELECT table_name FROM user_tables ORDER BY table_name")
                tables = cursor.fetchall()
                result = f"Oracle Tables ({len(tables)}):\n" + "\n".join(f"- {table[0]}" for table in tables)
            elif "select" in query.lower() and "employees" in query.lower():
                # Simple employee query
                if "engineering" in query.lower():
                    cursor.execute("SELECT * FROM employees WHERE department = 'Engineering'")
                else:
                    cursor.execute("SELECT * FROM employees")
                employees = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                result = f"Found {len(employees)} employees:\n"
                for emp in employees[:limit]:
                    result += json.dumps(dict(zip(columns, emp)), indent=2, default=str) + "\n"
            else:
                result = f"Oracle query processed: {query}\n(Implementation would handle specific SQL queries)"
            
            cursor.close()
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"🔴 Oracle Query Result:\n{result}"
                )]
            )
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Oracle query failed: {str(e)}"
                )]
            )
    
    async def _list_databases(self) -> CallToolResult:
        """List all available databases and their status."""
        status = []
        
        if self.mongodb_client:
            try:
                self.mongodb_client.admin.command('ping')
                status.append("✅ MongoDB: Connected")
            except:
                status.append("❌ MongoDB: Connection failed")
        else:
            status.append("❌ MongoDB: Not configured")
        
        if self.oracle_connection:
            try:
                cursor = self.oracle_connection.cursor()
                cursor.execute("SELECT 1 FROM DUAL")
                cursor.fetchone()
                cursor.close()
                status.append("✅ Oracle: Connected")
            except:
                status.append("❌ Oracle: Connection failed")
        else:
            status.append("❌ Oracle: Not configured")
        
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Database Status:\n" + "\n".join(status)
            )]
        )
    
    async def _get_database_info(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed information about a specific database."""
        database = arguments.get("database", "").lower()
        
        if database in ['mongodb', 'mongo', 'database a', 'database b']:
            if self.mongodb_client:
                try:
                    db_list = self.mongodb_client.list_database_names()
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"MongoDB Information:\n- Type: Document-based NoSQL\n- Databases: {len(db_list)}\n- Available: {', '.join(db_list[:5])}"
                        )]
                    )
                except Exception as e:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"MongoDB error: {str(e)}"
                        )]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="MongoDB not connected"
                    )]
                )
        elif database in ['oracle', 'database c']:
            if self.oracle_connection:
                try:
                    cursor = self.oracle_connection.cursor()
                    cursor.execute("SELECT COUNT(*) FROM user_tables")
                    table_count = cursor.fetchone()[0]
                    cursor.close()
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Oracle Information:\n- Type: Relational SQL\n- Tables: {table_count}\n- Status: Connected"
                        )]
                    )
                except Exception as e:
                    return CallToolResult(
                        content=[TextContent(
                            type="text",
                            text=f"Oracle error: {str(e)}"
                        )]
                    )
            else:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Oracle not connected"
                    )]
                )
        else:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Unknown database. Available: mongodb, oracle, database a/b/c"
                )]
            )
    
    # MongoDB-specific methods
    async def _mongodb_find(self, arguments: Dict[str, Any]) -> CallToolResult:
        """MongoDB find operation."""
        # Implementation would be similar to the separate MongoDB MCP server
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="MongoDB find operation (implementation details would go here)"
            )]
        )
    
    async def _mongodb_aggregate(self, arguments: Dict[str, Any]) -> CallToolResult:
        """MongoDB aggregate operation."""
        # Implementation would be similar to the separate MongoDB MCP server
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="MongoDB aggregate operation (implementation details would go here)"
            )]
        )
    
    # Oracle-specific methods
    async def _oracle_execute_sql(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Oracle SQL execution."""
        # Implementation would be similar to the separate Oracle MCP server
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Oracle SQL execution (implementation details would go here)"
            )]
        )
    
    async def _oracle_list_tables(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Oracle list tables."""
        # Implementation would be similar to the separate Oracle MCP server
        return CallToolResult(
            content=[TextContent(
                type="text",
                text="Oracle list tables (implementation details would go here)"
            )]
        )
    
    async def run(self):
        """Run the unified MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point."""
    server = UnifiedMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
