#!/usr/bin/env python3
"""
Test script for MongoDB MCP Server
This script tests the MongoDB MCP server functionality.
"""

import os
import sys
import asyncio
import json
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

async def test_mongodb_mcp_server():
    """Test the MongoDB MCP server."""
    print("Testing MongoDB MCP Server...")
    
    try:
        from mcp_servers.mongodb_mcp_server import MongoDBMCPServer
        
        # Create server instance
        server = MongoDBMCPServer()
        
        if not server.client:
            print("❌ MongoDB connection failed - check your connection string")
            return False
        
        print("✅ MongoDB MCP Server created successfully")
        print("✅ MongoDB connection established")
        
        # Test basic functionality
        print("\nTesting basic functionality...")
        
        # Test list databases
        print("Testing list databases...")
        result = await server._list_databases()
        print(f"Result: {result.content[0].text[:200]}...")
        
        # Test list collections (if any databases exist)
        db_list = server.client.list_database_names()
        if db_list and len(db_list) > 0:
            test_db = db_list[0]
            print(f"\nTesting list collections for database: {test_db}")
            result = await server._list_collections({"database": test_db})
            print(f"Result: {result.content[0].text[:200]}...")
        
        print("\n✅ MongoDB MCP Server tests completed successfully")
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import MongoDB MCP Server: {e}")
        return False
    except Exception as e:
        print(f"❌ MongoDB MCP Server test failed: {e}")
        return False

async def test_mcp_tools():
    """Test MCP tools functionality."""
    print("\nTesting MCP Tools...")
    
    try:
        from mcp_servers.mongodb_mcp_server import MongoDBMCPServer
        
        server = MongoDBMCPServer()
        
        if not server.client:
            print("❌ MongoDB connection failed")
            return False
        
        # Test list tools
        print("Testing list tools...")
        tools_result = await server.server.list_tools()
        print(f"Available tools: {len(tools_result.tools)}")
        
        for tool in tools_result.tools:
            print(f"- {tool.name}: {tool.description}")
        
        print("✅ MCP Tools test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ MCP Tools test failed: {e}")
        return False

async def main():
    """Main test function."""
    print("=" * 60)
    print("MongoDB MCP Server Test Suite")
    print("=" * 60)
    
    # Check environment
    connection_string = os.getenv("MDB_MCP_CONNECTION_STRING")
    if not connection_string:
        print("❌ MDB_MCP_CONNECTION_STRING not set")
        print("Please set your MongoDB connection string in .env file")
        return 1
    
    print(f"Using connection string: {connection_string.split('@')[0]}@***")
    
    # Run tests
    tests = [
        test_mongodb_mcp_server,
        test_mcp_tools
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if await test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! MongoDB MCP Server is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
