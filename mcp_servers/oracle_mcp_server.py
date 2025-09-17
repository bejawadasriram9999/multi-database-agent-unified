#!/usr/bin/env python3
"""
Oracle MCP Server for Multi-Database Agent
Provides MCP (Model Context Protocol) interface to Oracle databases.
"""

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional, Union
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

class OracleMCPServer:
    """Oracle MCP Server implementation."""
    
    def __init__(self):
        self.server = Server("oracle-mcp-server")
        self.connection = None
        self._setup_handlers()
        self._connect_to_oracle()
    
    def _connect_to_oracle(self):
        """Establish connection to Oracle database."""
        connection_string = os.environ.get("ORACLE_CONNECTION_STRING")
        
        if not connection_string:
            logger.error("ORACLE_CONNECTION_STRING environment variable not set")
            return
        
        try:
            # Parse connection string (format: user/password@host:port/service_name)
            self.connection = oracledb.connect(connection_string)
            logger.info("Successfully connected to Oracle database")
        except Exception as e:
            logger.error(f"Failed to connect to Oracle database: {e}")
            self.connection = None
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available Oracle tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="oracle_execute_query",
                        description="Execute a SQL query on Oracle database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "SQL query to execute"
                                },
                                "query_type": {
                                    "type": "string",
                                    "enum": ["SELECT", "INSERT", "UPDATE", "DELETE", "DDL"],
                                    "description": "Type of SQL query"
                                }
                            },
                            "required": ["query", "query_type"]
                        }
                    ),
                    Tool(
                        name="oracle_list_tables",
                        description="List all tables in the Oracle database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "schema": {
                                    "type": "string",
                                    "description": "Schema name (optional, defaults to current user)"
                                }
                            }
                        }
                    ),
                    Tool(
                        name="oracle_describe_table",
                        description="Get table structure and column information",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {
                                    "type": "string",
                                    "description": "Name of the table to describe"
                                },
                                "schema": {
                                    "type": "string",
                                    "description": "Schema name (optional)"
                                }
                            },
                            "required": ["table_name"]
                        }
                    ),
                    Tool(
                        name="oracle_list_schemas",
                        description="List all schemas in the Oracle database",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="oracle_get_table_info",
                        description="Get detailed information about a table including constraints and indexes",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "table_name": {
                                    "type": "string",
                                    "description": "Name of the table"
                                },
                                "schema": {
                                    "type": "string",
                                    "description": "Schema name (optional)"
                                }
                            },
                            "required": ["table_name"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            if not self.connection:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Error: Not connected to Oracle database. Please check connection string."
                    )]
                )
            
            try:
                if name == "oracle_execute_query":
                    return await self._execute_query(arguments)
                elif name == "oracle_list_tables":
                    return await self._list_tables(arguments)
                elif name == "oracle_describe_table":
                    return await self._describe_table(arguments)
                elif name == "oracle_list_schemas":
                    return await self._list_schemas(arguments)
                elif name == "oracle_get_table_info":
                    return await self._get_table_info(arguments)
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
    
    async def _execute_query(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Execute a SQL query."""
        query = arguments.get("query", "")
        query_type = arguments.get("query_type", "SELECT")
        
        if not query:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: No query provided"
                )]
            )
        
        try:
            cursor = self.connection.cursor()
            
            if query_type.upper() == "SELECT":
                cursor.execute(query)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                
                # Format results as JSON
                formatted_results = []
                for row in results:
                    row_dict = dict(zip(columns, row))
                    formatted_results.append(row_dict)
                
                result_text = f"Query executed successfully. Found {len(formatted_results)} rows.\n\n"
                result_text += f"Columns: {', '.join(columns)}\n\n"
                result_text += f"Results:\n{json.dumps(formatted_results, indent=2, default=str)}"
                
            else:
                # For non-SELECT queries
                cursor.execute(query)
                self.connection.commit()
                result_text = f"{query_type} query executed successfully. Rows affected: {cursor.rowcount}"
            
            cursor.close()
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Query execution failed: {str(e)}"
                )]
            )
    
    async def _list_tables(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List all tables in the database."""
        schema = arguments.get("schema")
        
        try:
            cursor = self.connection.cursor()
            
            if schema:
                query = """
                SELECT table_name, num_rows, last_analyzed
                FROM all_tables 
                WHERE owner = :schema
                ORDER BY table_name
                """
                cursor.execute(query, [schema])
            else:
                query = """
                SELECT table_name, num_rows, last_analyzed
                FROM user_tables
                ORDER BY table_name
                """
                cursor.execute(query)
            
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                result_text = f"No tables found in schema: {schema or 'current user'}"
            else:
                result_text = f"Tables in schema '{schema or 'current user'}':\n\n"
                for table_name, num_rows, last_analyzed in results:
                    result_text += f"- {table_name}"
                    if num_rows:
                        result_text += f" ({num_rows:,} rows)"
                    if last_analyzed:
                        result_text += f" [Last analyzed: {last_analyzed}]"
                    result_text += "\n"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to list tables: {str(e)}"
                )]
            )
    
    async def _describe_table(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Describe table structure."""
        table_name = arguments.get("table_name", "")
        schema = arguments.get("schema")
        
        if not table_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: No table name provided"
                )]
            )
        
        try:
            cursor = self.connection.cursor()
            
            # Get column information
            if schema:
                query = """
                SELECT column_name, data_type, data_length, nullable, data_default
                FROM all_tab_columns
                WHERE table_name = :table_name AND owner = :schema
                ORDER BY column_id
                """
                cursor.execute(query, [table_name.upper(), schema.upper()])
            else:
                query = """
                SELECT column_name, data_type, data_length, nullable, data_default
                FROM user_tab_columns
                WHERE table_name = :table_name
                ORDER BY column_id
                """
                cursor.execute(query, [table_name.upper()])
            
            columns = cursor.fetchall()
            cursor.close()
            
            if not columns:
                result_text = f"Table '{table_name}' not found in schema '{schema or 'current user'}'"
            else:
                result_text = f"Table Structure: {table_name}\n"
                if schema:
                    result_text += f"Schema: {schema}\n"
                result_text += "\nColumns:\n"
                result_text += "-" * 80 + "\n"
                result_text += f"{'Column Name':<30} {'Data Type':<20} {'Length':<10} {'Nullable':<10} {'Default'}\n"
                result_text += "-" * 80 + "\n"
                
                for col_name, data_type, data_length, nullable, data_default in columns:
                    nullable_str = "YES" if nullable == "Y" else "NO"
                    default_str = str(data_default) if data_default else ""
                    result_text += f"{col_name:<30} {data_type:<20} {data_length:<10} {nullable_str:<10} {default_str}\n"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to describe table: {str(e)}"
                )]
            )
    
    async def _list_schemas(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List all schemas in the database."""
        try:
            cursor = self.connection.cursor()
            query = """
            SELECT username, created, account_status
            FROM all_users
            WHERE username NOT IN ('SYS', 'SYSTEM', 'OUTLN', 'DIP', 'TSMSYS', 'DBSNMP', 'WMSYS', 'APPQOSSYS', 'APEX_030200', 'FLOWS_FILES', 'MDSYS', 'CTXSYS', 'XDB', 'ANONYMOUS', 'XS$NULL', 'ORDPLUGINS', 'ORDDATA', 'SI_INFORMTN_SCHEMA', 'OLAPSYS', 'MDDATA', 'SPATIAL_CSW_ADMIN_USR', 'SPATIAL_WFS_ADMIN_USR')
            ORDER BY username
            """
            cursor.execute(query)
            results = cursor.fetchall()
            cursor.close()
            
            if not results:
                result_text = "No user schemas found"
            else:
                result_text = "Available Schemas:\n\n"
                for username, created, account_status in results:
                    result_text += f"- {username} (Created: {created}, Status: {account_status})\n"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to list schemas: {str(e)}"
                )]
            )
    
    async def _get_table_info(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get detailed table information including constraints and indexes."""
        table_name = arguments.get("table_name", "")
        schema = arguments.get("schema")
        
        if not table_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: No table name provided"
                )]
            )
        
        try:
            cursor = self.connection.cursor()
            result_text = f"Detailed Information for Table: {table_name}\n"
            if schema:
                result_text += f"Schema: {schema}\n"
            result_text += "=" * 60 + "\n\n"
            
            # Get constraints
            if schema:
                constraint_query = """
                SELECT constraint_name, constraint_type, search_condition
                FROM all_constraints
                WHERE table_name = :table_name AND owner = :schema
                """
                cursor.execute(constraint_query, [table_name.upper(), schema.upper()])
            else:
                constraint_query = """
                SELECT constraint_name, constraint_type, search_condition
                FROM user_constraints
                WHERE table_name = :table_name
                """
                cursor.execute(constraint_query, [table_name.upper()])
            
            constraints = cursor.fetchall()
            
            if constraints:
                result_text += "Constraints:\n"
                for constraint_name, constraint_type, search_condition in constraints:
                    result_text += f"- {constraint_name}: {constraint_type}"
                    if search_condition:
                        result_text += f" ({search_condition})"
                    result_text += "\n"
                result_text += "\n"
            
            # Get indexes
            if schema:
                index_query = """
                SELECT index_name, index_type, uniqueness
                FROM all_indexes
                WHERE table_name = :table_name AND owner = :schema
                """
                cursor.execute(index_query, [table_name.upper(), schema.upper()])
            else:
                index_query = """
                SELECT index_name, index_type, uniqueness
                FROM user_indexes
                WHERE table_name = :table_name
                """
                cursor.execute(index_query, [table_name.upper()])
            
            indexes = cursor.fetchall()
            
            if indexes:
                result_text += "Indexes:\n"
                for index_name, index_type, uniqueness in indexes:
                    result_text += f"- {index_name}: {index_type} ({uniqueness})\n"
                result_text += "\n"
            
            cursor.close()
            
            if not constraints and not indexes:
                result_text += "No constraints or indexes found for this table.\n"
            
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=result_text
                )]
            )
            
        except Exception as e:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text=f"Failed to get table info: {str(e)}"
                )]
            )
    
    async def run(self):
        """Run the MCP server."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point."""
    server = OracleMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
