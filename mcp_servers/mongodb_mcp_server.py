#!/usr/bin/env python3
"""
MongoDB MCP Server for Multi-Database Agent
Provides MCP (Model Context Protocol) interface to MongoDB databases.
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

class MongoDBMCPServer:
    """MongoDB MCP Server implementation."""
    
    def __init__(self):
        self.server = Server("mongodb-mcp-server")
        self.client = None
        self._setup_handlers()
        self._connect_to_mongodb()
    
    def _connect_to_mongodb(self):
        """Establish connection to MongoDB database."""
        connection_string = os.environ.get("MDB_MCP_CONNECTION_STRING")
        
        if not connection_string:
            logger.error("MDB_MCP_CONNECTION_STRING environment variable not set")
            return
        
        try:
            # Parse connection string and connect
            self.client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
            
            # Test connection
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB database")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB database: {e}")
            self.client = None
    
    def _setup_handlers(self):
        """Setup MCP server handlers."""
        
        @self.server.list_tools()
        async def handle_list_tools() -> ListToolsResult:
            """List available MongoDB tools."""
            return ListToolsResult(
                tools=[
                    Tool(
                        name="mongodb_list_databases",
                        description="List all databases in MongoDB",
                        inputSchema={
                            "type": "object",
                            "properties": {}
                        }
                    ),
                    Tool(
                        name="mongodb_list_collections",
                        description="List all collections in a database",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                }
                            },
                            "required": ["database"]
                        }
                    ),
                    Tool(
                        name="mongodb_find_documents",
                        description="Find documents in a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "query": {
                                    "type": "object",
                                    "description": "MongoDB query filter (JSON object)"
                                },
                                "limit": {
                                    "type": "integer",
                                    "description": "Maximum number of documents to return",
                                    "default": 10
                                },
                                "sort": {
                                    "type": "object",
                                    "description": "Sort specification (JSON object)"
                                },
                                "projection": {
                                    "type": "object",
                                    "description": "Field projection (JSON object)"
                                }
                            },
                            "required": ["database", "collection"]
                        }
                    ),
                    Tool(
                        name="mongodb_find_one_document",
                        description="Find a single document in a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "query": {
                                    "type": "object",
                                    "description": "MongoDB query filter (JSON object)"
                                },
                                "projection": {
                                    "type": "object",
                                    "description": "Field projection (JSON object)"
                                }
                            },
                            "required": ["database", "collection"]
                        }
                    ),
                    Tool(
                        name="mongodb_count_documents",
                        description="Count documents in a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "query": {
                                    "type": "object",
                                    "description": "MongoDB query filter (JSON object)"
                                }
                            },
                            "required": ["database", "collection"]
                        }
                    ),
                    Tool(
                        name="mongodb_aggregate",
                        description="Run aggregation pipeline on a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "pipeline": {
                                    "type": "array",
                                    "description": "Aggregation pipeline stages",
                                    "items": {
                                        "type": "object"
                                    }
                                },
                                "allowDiskUse": {
                                    "type": "boolean",
                                    "description": "Allow disk use for large operations",
                                    "default": False
                                }
                            },
                            "required": ["database", "collection", "pipeline"]
                        }
                    ),
                    Tool(
                        name="mongodb_insert_document",
                        description="Insert a document into a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "document": {
                                    "type": "object",
                                    "description": "Document to insert (JSON object)"
                                }
                            },
                            "required": ["database", "collection", "document"]
                        }
                    ),
                    Tool(
                        name="mongodb_insert_many_documents",
                        description="Insert multiple documents into a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "documents": {
                                    "type": "array",
                                    "description": "Documents to insert (array of JSON objects)",
                                    "items": {
                                        "type": "object"
                                    }
                                }
                            },
                            "required": ["database", "collection", "documents"]
                        }
                    ),
                    Tool(
                        name="mongodb_update_document",
                        description="Update a document in a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "query": {
                                    "type": "object",
                                    "description": "Query to find document to update"
                                },
                                "update": {
                                    "type": "object",
                                    "description": "Update operations"
                                },
                                "upsert": {
                                    "type": "boolean",
                                    "description": "Create document if it doesn't exist",
                                    "default": False
                                }
                            },
                            "required": ["database", "collection", "query", "update"]
                        }
                    ),
                    Tool(
                        name="mongodb_delete_document",
                        description="Delete a document from a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "query": {
                                    "type": "object",
                                    "description": "Query to find document to delete"
                                }
                            },
                            "required": ["database", "collection", "query"]
                        }
                    ),
                    Tool(
                        name="mongodb_create_index",
                        description="Create an index on a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "index_spec": {
                                    "type": "object",
                                    "description": "Index specification"
                                },
                                "index_options": {
                                    "type": "object",
                                    "description": "Index options (unique, sparse, etc.)"
                                }
                            },
                            "required": ["database", "collection", "index_spec"]
                        }
                    ),
                    Tool(
                        name="mongodb_list_indexes",
                        description="List indexes on a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                }
                            },
                            "required": ["database", "collection"]
                        }
                    ),
                    Tool(
                        name="mongodb_drop_index",
                        description="Drop an index from a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "index_name": {
                                    "type": "string",
                                    "description": "Name of index to drop"
                                }
                            },
                            "required": ["database", "collection", "index_name"]
                        }
                    ),
                    Tool(
                        name="mongodb_get_collection_stats",
                        description="Get statistics about a collection",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                }
                            },
                            "required": ["database", "collection"]
                        }
                    ),
                    Tool(
                        name="mongodb_explain_query",
                        description="Explain the execution plan for a query",
                        inputSchema={
                            "type": "object",
                            "properties": {
                                "database": {
                                    "type": "string",
                                    "description": "Database name"
                                },
                                "collection": {
                                    "type": "string",
                                    "description": "Collection name"
                                },
                                "query": {
                                    "type": "object",
                                    "description": "Query to explain"
                                },
                                "sort": {
                                    "type": "object",
                                    "description": "Sort specification"
                                }
                            },
                            "required": ["database", "collection", "query"]
                        }
                    )
                ]
            )
        
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> CallToolResult:
            """Handle tool calls."""
            if not self.client:
                return CallToolResult(
                    content=[TextContent(
                        type="text",
                        text="Error: Not connected to MongoDB database. Please check connection string."
                    )]
                )
            
            try:
                if name == "mongodb_list_databases":
                    return await self._list_databases()
                elif name == "mongodb_list_collections":
                    return await self._list_collections(arguments)
                elif name == "mongodb_find_documents":
                    return await self._find_documents(arguments)
                elif name == "mongodb_find_one_document":
                    return await self._find_one_document(arguments)
                elif name == "mongodb_count_documents":
                    return await self._count_documents(arguments)
                elif name == "mongodb_aggregate":
                    return await self._aggregate(arguments)
                elif name == "mongodb_insert_document":
                    return await self._insert_document(arguments)
                elif name == "mongodb_insert_many_documents":
                    return await self._insert_many_documents(arguments)
                elif name == "mongodb_update_document":
                    return await self._update_document(arguments)
                elif name == "mongodb_delete_document":
                    return await self._delete_document(arguments)
                elif name == "mongodb_create_index":
                    return await self._create_index(arguments)
                elif name == "mongodb_list_indexes":
                    return await self._list_indexes(arguments)
                elif name == "mongodb_drop_index":
                    return await self._drop_index(arguments)
                elif name == "mongodb_get_collection_stats":
                    return await self._get_collection_stats(arguments)
                elif name == "mongodb_explain_query":
                    return await self._explain_query(arguments)
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
    
    async def _list_databases(self) -> CallToolResult:
        """List all databases."""
        try:
            db_list = self.client.list_database_names()
            result_text = f"Available databases ({len(db_list)}):\n\n"
            for db_name in db_list:
                result_text += f"- {db_name}\n"
            
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
                    text=f"Failed to list databases: {str(e)}"
                )]
            )
    
    async def _list_collections(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List collections in a database."""
        database_name = arguments.get("database", "")
        
        if not database_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: No database name provided"
                )]
            )
        
        try:
            db = self.client[database_name]
            collections = db.list_collection_names()
            
            if not collections:
                result_text = f"No collections found in database '{database_name}'"
            else:
                result_text = f"Collections in database '{database_name}' ({len(collections)}):\n\n"
                for collection_name in collections:
                    # Get collection stats
                    try:
                        stats = db.command("collStats", collection_name)
                        count = stats.get("count", 0)
                        size = stats.get("size", 0)
                        result_text += f"- {collection_name} ({count:,} documents, {size:,} bytes)\n"
                    except:
                        result_text += f"- {collection_name}\n"
            
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
                    text=f"Failed to list collections: {str(e)}"
                )]
            )
    
    async def _find_documents(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Find documents in a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        query = arguments.get("query", {})
        limit = arguments.get("limit", 10)
        sort = arguments.get("sort")
        projection = arguments.get("projection")
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Build query
            cursor = collection.find(query)
            
            if projection:
                cursor = cursor.project(projection)
            
            if sort:
                cursor = cursor.sort(list(sort.items()))
            
            cursor = cursor.limit(limit)
            
            # Execute query
            documents = list(cursor)
            
            if not documents:
                result_text = f"No documents found in {database_name}.{collection_name}"
                if query:
                    result_text += f" with query: {json.dumps(query)}"
            else:
                result_text = f"Found {len(documents)} document(s) in {database_name}.{collection_name}:\n\n"
                for i, doc in enumerate(documents, 1):
                    result_text += f"Document {i}:\n"
                    result_text += json.dumps(doc, indent=2, default=json_util.default) + "\n\n"
            
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
                    text=f"Failed to find documents: {str(e)}"
                )]
            )
    
    async def _find_one_document(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Find a single document in a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        query = arguments.get("query", {})
        projection = arguments.get("projection")
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Build query
            cursor = collection.find(query)
            
            if projection:
                cursor = cursor.project(projection)
            
            # Execute query
            document = cursor.limit(1).next() if cursor.count() > 0 else None
            
            if not document:
                result_text = f"No document found in {database_name}.{collection_name}"
                if query:
                    result_text += f" with query: {json.dumps(query)}"
            else:
                result_text = f"Document found in {database_name}.{collection_name}:\n\n"
                result_text += json.dumps(document, indent=2, default=json_util.default)
            
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
                    text=f"Failed to find document: {str(e)}"
                )]
            )
    
    async def _count_documents(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Count documents in a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        query = arguments.get("query", {})
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            count = collection.count_documents(query)
            
            result_text = f"Document count in {database_name}.{collection_name}: {count:,}"
            if query:
                result_text += f" (with query: {json.dumps(query)})"
            
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
                    text=f"Failed to count documents: {str(e)}"
                )]
            )
    
    async def _aggregate(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Run aggregation pipeline."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        pipeline = arguments.get("pipeline", [])
        allow_disk_use = arguments.get("allowDiskUse", False)
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not pipeline:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Pipeline is required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Execute aggregation
            cursor = collection.aggregate(pipeline, allowDiskUse=allow_disk_use)
            results = list(cursor)
            
            if not results:
                result_text = f"No results from aggregation pipeline in {database_name}.{collection_name}"
            else:
                result_text = f"Aggregation results from {database_name}.{collection_name} ({len(results)} documents):\n\n"
                for i, doc in enumerate(results, 1):
                    result_text += f"Result {i}:\n"
                    result_text += json.dumps(doc, indent=2, default=json_util.default) + "\n\n"
            
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
                    text=f"Failed to run aggregation: {str(e)}"
                )]
            )
    
    async def _insert_document(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Insert a document into a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        document = arguments.get("document", {})
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not document:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Document is required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            result = collection.insert_one(document)
            
            result_text = f"Document inserted successfully into {database_name}.{collection_name}\n"
            result_text += f"Inserted ID: {result.inserted_id}\n"
            result_text += f"Document: {json.dumps(document, indent=2, default=json_util.default)}"
            
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
                    text=f"Failed to insert document: {str(e)}"
                )]
            )
    
    async def _insert_many_documents(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Insert multiple documents into a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        documents = arguments.get("documents", [])
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not documents:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Documents array is required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            result = collection.insert_many(documents)
            
            result_text = f"Documents inserted successfully into {database_name}.{collection_name}\n"
            result_text += f"Inserted {len(result.inserted_ids)} documents\n"
            result_text += f"Inserted IDs: {result.inserted_ids}"
            
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
                    text=f"Failed to insert documents: {str(e)}"
                )]
            )
    
    async def _update_document(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Update a document in a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        query = arguments.get("query", {})
        update = arguments.get("update", {})
        upsert = arguments.get("upsert", False)
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not query or not update:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Query and update are required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            result = collection.update_one(query, update, upsert=upsert)
            
            result_text = f"Update operation completed in {database_name}.{collection_name}\n"
            result_text += f"Matched: {result.matched_count} document(s)\n"
            result_text += f"Modified: {result.modified_count} document(s)\n"
            if upsert and result.upserted_id:
                result_text += f"Upserted ID: {result.upserted_id}\n"
            result_text += f"Query: {json.dumps(query)}\n"
            result_text += f"Update: {json.dumps(update)}"
            
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
                    text=f"Failed to update document: {str(e)}"
                )]
            )
    
    async def _delete_document(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Delete a document from a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        query = arguments.get("query", {})
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not query:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Query is required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            result = collection.delete_one(query)
            
            result_text = f"Delete operation completed in {database_name}.{collection_name}\n"
            result_text += f"Deleted: {result.deleted_count} document(s)\n"
            result_text += f"Query: {json.dumps(query)}"
            
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
                    text=f"Failed to delete document: {str(e)}"
                )]
            )
    
    async def _create_index(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Create an index on a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        index_spec = arguments.get("index_spec", {})
        index_options = arguments.get("index_options", {})
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not index_spec:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Index specification is required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Create index
            index_name = collection.create_index(
                list(index_spec.items()) if isinstance(index_spec, dict) else index_spec,
                **index_options
            )
            
            result_text = f"Index created successfully in {database_name}.{collection_name}\n"
            result_text += f"Index name: {index_name}\n"
            result_text += f"Index spec: {json.dumps(index_spec)}\n"
            if index_options:
                result_text += f"Index options: {json.dumps(index_options)}"
            
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
                    text=f"Failed to create index: {str(e)}"
                )]
            )
    
    async def _list_indexes(self, arguments: Dict[str, Any]) -> CallToolResult:
        """List indexes on a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            indexes = list(collection.list_indexes())
            
            if not indexes:
                result_text = f"No indexes found on {database_name}.{collection_name}"
            else:
                result_text = f"Indexes on {database_name}.{collection_name} ({len(indexes)}):\n\n"
                for index in indexes:
                    result_text += f"- {index['name']}: {json.dumps(index['key'])}\n"
                    if 'unique' in index:
                        result_text += f"  Unique: {index['unique']}\n"
                    if 'sparse' in index:
                        result_text += f"  Sparse: {index['sparse']}\n"
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
                    text=f"Failed to list indexes: {str(e)}"
                )]
            )
    
    async def _drop_index(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Drop an index from a collection."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        index_name = arguments.get("index_name", "")
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not index_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Index name is required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            collection.drop_index(index_name)
            
            result_text = f"Index '{index_name}' dropped successfully from {database_name}.{collection_name}"
            
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
                    text=f"Failed to drop index: {str(e)}"
                )]
            )
    
    async def _get_collection_stats(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Get collection statistics."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        try:
            db = self.client[database_name]
            stats = db.command("collStats", collection_name)
            
            result_text = f"Collection statistics for {database_name}.{collection_name}:\n\n"
            result_text += f"Documents: {stats.get('count', 0):,}\n"
            result_text += f"Size: {stats.get('size', 0):,} bytes\n"
            result_text += f"Average document size: {stats.get('avgObjSize', 0):,} bytes\n"
            result_text += f"Storage size: {stats.get('storageSize', 0):,} bytes\n"
            result_text += f"Indexes: {stats.get('nindexes', 0)}\n"
            result_text += f"Total index size: {stats.get('totalIndexSize', 0):,} bytes\n"
            
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
                    text=f"Failed to get collection stats: {str(e)}"
                )]
            )
    
    async def _explain_query(self, arguments: Dict[str, Any]) -> CallToolResult:
        """Explain query execution plan."""
        database_name = arguments.get("database", "")
        collection_name = arguments.get("collection", "")
        query = arguments.get("query", {})
        sort = arguments.get("sort")
        
        if not database_name or not collection_name:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Database and collection names are required"
                )]
            )
        
        if not query:
            return CallToolResult(
                content=[TextContent(
                    type="text",
                    text="Error: Query is required"
                )]
            )
        
        try:
            db = self.client[database_name]
            collection = db[collection_name]
            
            # Build explain query
            explain_query = {"query": query}
            if sort:
                explain_query["sort"] = sort
            
            explain_result = collection.find(query).explain()
            
            result_text = f"Query execution plan for {database_name}.{collection_name}:\n\n"
            result_text += f"Query: {json.dumps(query)}\n"
            if sort:
                result_text += f"Sort: {json.dumps(sort)}\n"
            result_text += f"\nExecution plan:\n"
            result_text += json.dumps(explain_result, indent=2, default=json_util.default)
            
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
                    text=f"Failed to explain query: {str(e)}"
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
    server = MongoDBMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
