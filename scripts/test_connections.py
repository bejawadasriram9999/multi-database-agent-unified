#!/usr/bin/env python3
"""
Test database connections for Multi-Database Agent
This script tests the configured database connections.
"""

import os
import sys
import logging
from typing import Dict, Any
from dotenv import load_dotenv

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_mongodb_connection() -> Dict[str, Any]:
    """Test MongoDB connection."""
    result = {
        "database": "MongoDB",
        "success": False,
        "error": None,
        "details": {}
    }
    
    connection_string = os.getenv("MDB_MCP_CONNECTION_STRING")
    if not connection_string:
        result["error"] = "MDB_MCP_CONNECTION_STRING not configured"
        return result
    
    try:
        import pymongo
        from pymongo import MongoClient
        
        logger.info("Testing MongoDB connection...")
        client = MongoClient(connection_string, serverSelectionTimeoutMS=5000)
        
        # Test connection
        client.admin.command('ping')
        
        # Get database info
        db_list = client.list_database_names()
        result["details"]["databases"] = db_list
        result["details"]["connection_string"] = connection_string.split('@')[0] + '@***'  # Hide credentials
        
        result["success"] = True
        logger.info("✅ MongoDB connection successful")
        
    except ImportError:
        result["error"] = "pymongo not installed"
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ MongoDB connection failed: {e}")
    
    return result

def test_oracle_connection() -> Dict[str, Any]:
    """Test Oracle connection."""
    result = {
        "database": "Oracle",
        "success": False,
        "error": None,
        "details": {}
    }
    
    connection_string = os.getenv("ORACLE_MCP_CONNECTION_STRING")
    if not connection_string:
        result["error"] = "ORACLE_MCP_CONNECTION_STRING not configured"
        return result
    
    try:
        import oracledb
        
        logger.info("Testing Oracle connection...")
        connection = oracledb.connect(connection_string)
        
        # Test connection
        cursor = connection.cursor()
        cursor.execute("SELECT 1 FROM DUAL")
        result_data = cursor.fetchone()
        
        # Get database info
        cursor.execute("SELECT USER FROM DUAL")
        current_user = cursor.fetchone()[0]
        
        cursor.execute("""
            SELECT COUNT(*) FROM all_tables WHERE owner = :user
        """, [current_user])
        table_count = cursor.fetchone()[0]
        
        result["details"]["current_user"] = current_user
        result["details"]["table_count"] = table_count
        result["details"]["connection_string"] = connection_string.split('@')[0] + '@***'  # Hide credentials
        
        cursor.close()
        connection.close()
        
        result["success"] = True
        logger.info("✅ Oracle connection successful")
        
    except ImportError:
        result["error"] = "oracledb not installed"
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ Oracle connection failed: {e}")
    
    return result

def test_google_api() -> Dict[str, Any]:
    """Test Google API configuration."""
    result = {
        "service": "Google API",
        "success": False,
        "error": None,
        "details": {}
    }
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        result["error"] = "GOOGLE_API_KEY not configured"
        return result
    
    try:
        # Test if we can import Google ADK
        from google.adk.agents import LlmAgent
        
        result["details"]["api_key_configured"] = True
        result["details"]["adk_available"] = True
        result["success"] = True
        logger.info("✅ Google API configuration successful")
        
    except ImportError:
        result["error"] = "google-adk not installed"
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ Google API configuration failed: {e}")
    
    return result

def test_mcp_servers() -> Dict[str, Any]:
    """Test MCP server availability."""
    result = {
        "service": "MCP Servers",
        "success": False,
        "error": None,
        "details": {}
    }
    
    try:
        # Test if our MongoDB MCP server can be imported
        try:
            from mcp_servers.mongodb_mcp_server import MongoDBMCPServer
            result["details"]["mongodb_mcp_available"] = True
        except ImportError as e:
            result["details"]["mongodb_mcp_available"] = False
            result["details"]["mongodb_mcp_error"] = str(e)
        
        # Test if our Oracle MCP server can be imported
        try:
            from mcp_servers.oracle_mcp_server import OracleMCPServer
            result["details"]["oracle_mcp_available"] = True
        except ImportError as e:
            result["details"]["oracle_mcp_available"] = False
            result["details"]["oracle_mcp_error"] = str(e)
        
        # Test MCP library availability
        try:
            import mcp
            result["details"]["mcp_library_available"] = True
        except ImportError:
            result["details"]["mcp_library_available"] = False
        
        result["success"] = True
        logger.info("✅ MCP servers test completed")
        
    except Exception as e:
        result["error"] = str(e)
        logger.error(f"❌ MCP servers test failed: {e}")
    
    return result

def main():
    """Run all connection tests."""
    print("=" * 60)
    print("Multi-Database Agent Connection Tests")
    print("=" * 60)
    
    tests = [
        test_mongodb_connection,
        test_oracle_connection,
        test_google_api,
        test_mcp_servers
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test_func.__name__} failed with exception: {e}")
            results.append({
                "service": test_func.__name__,
                "success": False,
                "error": str(e),
                "details": {}
            })
    
    # Print summary
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    successful_tests = 0
    total_tests = len(results)
    
    for result in results:
        service_name = result.get("database") or result.get("service", "Unknown")
        if result["success"]:
            print(f"✅ {service_name}: SUCCESS")
            successful_tests += 1
        else:
            print(f"❌ {service_name}: FAILED - {result['error']}")
        
        # Print details if available
        if result.get("details"):
            for key, value in result["details"].items():
                print(f"   {key}: {value}")
    
    print("\n" + "=" * 60)
    print(f"Overall Result: {successful_tests}/{total_tests} tests passed")
    
    if successful_tests == total_tests:
        print("🎉 All tests passed! Your setup is ready.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check your configuration.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
