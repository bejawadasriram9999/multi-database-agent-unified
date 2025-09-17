#!/usr/bin/env python3
"""
Demo Multi-Database Agent
This script demonstrates the agent's capabilities with simulated responses.
"""

import os
import sys
import asyncio
import json
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class AgentDemo:
    """Demo the multi-database agent capabilities."""
    
    def __init__(self):
        self.demo_queries = [
            {
                "category": "MongoDB Queries",
                "queries": [
                    {
                        "query": "Show me all databases in MongoDB",
                        "expected_response": "I'll query MongoDB to list all available databases. Let me connect to the MongoDB MCP server and retrieve the database list.",
                        "database": "MongoDB"
                    },
                    {
                        "query": "Find all users with status 'active' in the users collection",
                        "expected_response": "I'll search the users collection in MongoDB for documents where status equals 'active'. This will use the MongoDB find operation.",
                        "database": "MongoDB"
                    },
                    {
                        "query": "Count products by category",
                        "expected_response": "I'll run an aggregation pipeline on the products collection to group by category and count documents in each group.",
                        "database": "MongoDB"
                    },
                    {
                        "query": "Create an index on the email field in the users collection",
                        "expected_response": "I'll create a unique index on the email field in the users collection to improve query performance and ensure email uniqueness.",
                        "database": "MongoDB"
                    }
                ]
            },
            {
                "category": "Oracle Queries",
                "queries": [
                    {
                        "query": "Show me all tables in the database",
                        "expected_response": "I'll query the Oracle database to list all tables in the current schema using the Oracle MCP server.",
                        "database": "Oracle"
                    },
                    {
                        "query": "SELECT * FROM employees WHERE department = 'Engineering'",
                        "expected_response": "I'll execute this SQL query on the Oracle database to retrieve all employees in the Engineering department.",
                        "database": "Oracle"
                    },
                    {
                        "query": "Show me the average salary by department",
                        "expected_response": "I'll run a SQL query with GROUP BY to calculate the average salary for each department in the employees table.",
                        "database": "Oracle"
                    },
                    {
                        "query": "Describe the structure of the employees table",
                        "expected_response": "I'll query the Oracle data dictionary to show the column structure, data types, and constraints of the employees table.",
                        "database": "Oracle"
                    }
                ]
            },
            {
                "category": "Intelligent Routing",
                "queries": [
                    {
                        "query": "Find all employees",
                        "expected_response": "I need to clarify which database you'd like me to query. I can search for employees in:\n- MongoDB (users collection)\n- Oracle (employees table)\n\nPlease specify which database or use 'Database A/B' for MongoDB or 'Database C' for Oracle.",
                        "database": "Unknown - Needs Clarification"
                    },
                    {
                        "query": "Query database A for all users",
                        "expected_response": "I'll query Database A (MongoDB) to retrieve all users from the users collection.",
                        "database": "MongoDB (Database A)"
                    },
                    {
                        "query": "Query database C for all employees",
                        "expected_response": "I'll query Database C (Oracle) to retrieve all employees from the employees table.",
                        "database": "Oracle (Database C)"
                    },
                    {
                        "query": "db.users.find({status: 'active'})",
                        "expected_response": "I recognize this as MongoDB query syntax. I'll execute this find operation on the users collection in MongoDB.",
                        "database": "MongoDB"
                    }
                ]
            },
            {
                "category": "Advanced Operations",
                "queries": [
                    {
                        "query": "Show me the top 5 highest paid employees",
                        "expected_response": "I'll query the Oracle employees table, order by salary in descending order, and limit to 5 results.",
                        "database": "Oracle"
                    },
                    {
                        "query": "Find users who have 'Python' in their skills array",
                        "expected_response": "I'll use MongoDB's array query operators to find users where the skills array contains 'Python'.",
                        "database": "MongoDB"
                    },
                    {
                        "query": "Show me sales data grouped by month and region",
                        "expected_response": "I'll run a SQL query with GROUP BY to aggregate sales data by month and region from the Oracle sales table.",
                        "database": "Oracle"
                    },
                    {
                        "query": "Create a compound index on department and status in the users collection",
                        "expected_response": "I'll create a compound index on both department and status fields in the MongoDB users collection for efficient multi-field queries.",
                        "database": "MongoDB"
                    }
                ]
            }
        ]
    
    def print_header(self):
        """Print demo header."""
        print("=" * 80)
        print("🤖 MULTI-DATABASE AGENT DEMO")
        print("=" * 80)
        print("This demo shows how the agent intelligently routes queries to the")
        print("appropriate database (MongoDB or Oracle) based on query patterns.")
        print("=" * 80)
    
    def print_query_demo(self, category: str, queries: List[Dict]):
        """Print a category of query demos."""
        print(f"\n📂 {category}")
        print("-" * 60)
        
        for i, query_info in enumerate(queries, 1):
            print(f"\n{i}. Query: {query_info['query']}")
            print(f"   Database: {query_info['database']}")
            print(f"   Agent Response: {query_info['expected_response']}")
    
    def print_architecture_demo(self):
        """Print architecture demonstration."""
        print("\n" + "=" * 80)
        print("🏗️  ARCHITECTURE DEMONSTRATION")
        print("=" * 80)
        
        print("""
┌─────────────────────────────────────────────────────────────────┐
│                    USER QUERY                                  │
│              "Find all active users"                           │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              MULTI-DATABASE AGENT                              │
│              (Gemini 2.0 Flash)                                │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATABASE ROUTER                                   │
│         Analyzes query patterns and keywords                   │
│         • "users" → MongoDB                                    │
│         • "active" → Filter condition                          │
│         • No SQL keywords → MongoDB query                      │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              MONGODB MCP SERVER                                │
│         Executes: db.users.find({status: "active"})            │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│              MONGODB DATABASE                                  │
│         Returns: List of active users                          │
└─────────────────────────────────────────────────────────────────┘
        """)
    
    def print_capabilities_demo(self):
        """Print capabilities demonstration."""
        print("\n" + "=" * 80)
        print("🚀 AGENT CAPABILITIES")
        print("=" * 80)
        
        capabilities = [
            {
                "feature": "Intelligent Database Routing",
                "description": "Automatically determines which database to query based on query patterns, keywords, and syntax",
                "examples": [
                    "MongoDB syntax → MongoDB",
                    "SQL syntax → Oracle", 
                    "Collection mentions → MongoDB",
                    "Table mentions → Oracle"
                ]
            },
            {
                "feature": "Multi-Database Support",
                "description": "Seamlessly works with both MongoDB and Oracle databases",
                "examples": [
                    "MongoDB: Document queries, aggregations, indexing",
                    "Oracle: SQL queries, joins, constraints, procedures"
                ]
            },
            {
                "feature": "Natural Language Processing",
                "description": "Understands natural language queries and converts them to appropriate database operations",
                "examples": [
                    "Show me all users → MongoDB find operation",
                    "Get employee count by department → Oracle GROUP BY query"
                ]
            },
            {
                "feature": "Advanced Query Operations",
                "description": "Supports complex operations across both database types",
                "examples": [
                    "MongoDB: Aggregation pipelines, text search, array operations",
                    "Oracle: Complex joins, subqueries, analytical functions"
                ]
            },
            {
                "feature": "Production Ready",
                "description": "Built with enterprise-grade features and security",
                "examples": [
                    "Error handling and logging",
                    "Connection pooling and timeouts",
                    "Input validation and sanitization",
                    "Audit trails and monitoring"
                ]
            }
        ]
        
        for i, capability in enumerate(capabilities, 1):
            print(f"\n{i}. {capability['feature']}")
            print(f"   {capability['description']}")
            print("   Examples:")
            for example in capability['examples']:
                print(f"   • {example}")
    
    def print_usage_examples(self):
        """Print usage examples."""
        print("\n" + "=" * 80)
        print("💡 USAGE EXAMPLES")
        print("=" * 80)
        
        print("""
🔹 Web Interface (Streamlit):
   streamlit run chat_ui.py
   → Open http://localhost:8501

🔹 REST API (FastAPI):
   python api_server.py
   → Open http://localhost:8000/docs

🔹 Google ADK CLI:
   adk web
   → Use the ADK web interface

🔹 Direct API Calls:
   curl -X POST "http://localhost:8000/query" \\
        -H "Content-Type: application/json" \\
        -d '{"query": "Find all active users"}'
        """)
    
    def print_setup_instructions(self):
        """Print setup instructions."""
        print("\n" + "=" * 80)
        print("🛠️  SETUP INSTRUCTIONS")
        print("=" * 80)
        
        print("""
1. 📋 Prerequisites:
   • Python 3.13+
   • MongoDB (Atlas or local)
   • Oracle database access
   • Google API key

2. 🔧 Installation:
   cd google-adk-with-mongo-db-mcp-server
   pip install -r requirements.txt
   cp example.env .env

3. ⚙️  Configuration:
   Edit .env file with your database connections:
   • MDB_MCP_CONNECTION_STRING=mongodb://...
   • ORACLE_MCP_CONNECTION_STRING=user/pass@host:port/service
   • GOOGLE_API_KEY=your_api_key

4. 🧪 Testing:
   python scripts/create_dummy_data.py
   python scripts/test_agent_with_dummy_data.py

5. 🚀 Running:
   streamlit run chat_ui.py
   python api_server.py
        """)
    
    def run_demo(self):
        """Run the complete demo."""
        self.print_header()
        
        # Print each category of queries
        for category_data in self.demo_queries:
            self.print_query_demo(category_data["category"], category_data["queries"])
        
        # Print architecture demo
        self.print_architecture_demo()
        
        # Print capabilities demo
        self.print_capabilities_demo()
        
        # Print usage examples
        self.print_usage_examples()
        
        # Print setup instructions
        self.print_setup_instructions()
        
        print("\n" + "=" * 80)
        print("🎉 DEMO COMPLETE!")
        print("=" * 80)
        print("The Multi-Database Agent is ready to intelligently route your")
        print("queries between MongoDB and Oracle databases!")
        print("=" * 80)

def main():
    """Main demo function."""
    demo = AgentDemo()
    demo.run_demo()
    return 0

if __name__ == "__main__":
    sys.exit(main())
