#!/usr/bin/env python3
"""
Test Multi-Database Agent with Dummy Data
This script demonstrates the agent's capabilities with the created dummy data.
"""

import os
import sys
import asyncio
import json
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

class AgentTester:
    """Test the multi-database agent with various queries."""
    
    def __init__(self):
        self.agent = None
        self.test_results = []
    
    async def initialize_agent(self):
        """Initialize the multi-database agent."""
        try:
            from mongodb_agent.agent import multi_db_agent
            self.agent = multi_db_agent.get_agent()
            print("✅ Multi-database agent initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize agent: {e}")
            return False
    
    async def run_test(self, test_name: str, query: str, expected_db: str = None):
        """Run a single test and record results."""
        print(f"\n🧪 Testing: {test_name}")
        print(f"Query: {query}")
        
        try:
            # Run the query through the agent
            response = self.agent.run(query)
            
            result = {
                "test_name": test_name,
                "query": query,
                "expected_db": expected_db,
                "success": True,
                "response": response,
                "response_length": len(response) if response else 0
            }
            
            print(f"✅ Success - Response length: {result['response_length']} characters")
            if response:
                # Show first 200 characters of response
                preview = response[:200] + "..." if len(response) > 200 else response
                print(f"Response preview: {preview}")
            
            self.test_results.append(result)
            return True
            
        except Exception as e:
            result = {
                "test_name": test_name,
                "query": query,
                "expected_db": expected_db,
                "success": False,
                "error": str(e),
                "response": None
            }
            
            print(f"❌ Failed: {e}")
            self.test_results.append(result)
            return False
    
    async def run_mongodb_tests(self):
        """Run MongoDB-specific tests."""
        print("\n" + "="*60)
        print("MONGODB TESTS")
        print("="*60)
        
        mongodb_tests = [
            ("List all databases", "Show me all databases in MongoDB", "MongoDB"),
            ("List collections", "List all collections in the test_company_db database", "MongoDB"),
            ("Find active users", "Find all users with status 'active' in the users collection", "MongoDB"),
            ("Count products by category", "Count how many products are in each category", "MongoDB"),
            ("Find recent orders", "Find the 5 most recent orders", "MongoDB"),
            ("Aggregate sales by month", "Show me total sales by month from the analytics collection", "MongoDB"),
            ("Find users by department", "Find all users in the Engineering department", "MongoDB"),
            ("Product price range", "Find products with price between 100 and 500", "MongoDB"),
            ("User skills analysis", "Show me users who have Python in their skills", "MongoDB"),
            ("Order status summary", "Count orders by status", "MongoDB")
        ]
        
        for test_name, query, expected_db in mongodb_tests:
            await self.run_test(test_name, query, expected_db)
    
    async def run_oracle_tests(self):
        """Run Oracle-specific tests."""
        print("\n" + "="*60)
        print("ORACLE TESTS")
        print("="*60)
        
        oracle_tests = [
            ("List all tables", "Show me all tables in the test_company schema", "Oracle"),
            ("Employee count by department", "SELECT department, COUNT(*) FROM employees GROUP BY department", "Oracle"),
            ("High salary employees", "SELECT * FROM employees WHERE salary > 100000", "Oracle"),
            ("Active projects", "SELECT * FROM projects WHERE status = 'In Progress'", "Oracle"),
            ("Sales by region", "SELECT region, SUM(total_amount) FROM sales GROUP BY region", "Oracle"),
            ("Department budgets", "SELECT department_name, budget FROM departments ORDER BY budget DESC", "Oracle"),
            ("Recent hires", "SELECT * FROM employees WHERE hire_date > SYSDATE - 30", "Oracle"),
            ("Project budget analysis", "SELECT AVG(budget), MAX(budget), MIN(budget) FROM projects", "Oracle"),
            ("Top sales performers", "SELECT employee_id, SUM(total_amount) FROM sales GROUP BY employee_id ORDER BY SUM(total_amount) DESC", "Oracle"),
            ("Employee details with manager", "SELECT e.first_name, e.last_name, m.first_name as manager_name FROM employees e LEFT JOIN employees m ON e.manager_id = m.employee_id", "Oracle")
        ]
        
        for test_name, query, expected_db in oracle_tests:
            await self.run_test(test_name, query, expected_db)
    
    async def run_intelligent_routing_tests(self):
        """Run tests that demonstrate intelligent database routing."""
        print("\n" + "="*60)
        print("INTELLIGENT ROUTING TESTS")
        print("="*60)
        
        routing_tests = [
            ("MongoDB query detection", "Find all users in the Engineering department", "MongoDB"),
            ("Oracle query detection", "SELECT * FROM employees WHERE department = 'Engineering'", "Oracle"),
            ("Ambiguous query", "Show me all employees", None),  # Should ask for clarification
            ("Database A mention", "Query database A for all users", "MongoDB"),
            ("Database C mention", "Query database C for all employees", "Oracle"),
            ("Collection mention", "Show me all documents in the products collection", "MongoDB"),
            ("Table mention", "Show me all records in the employees table", "Oracle"),
            ("MongoDB syntax", "db.users.find({status: 'active'})", "MongoDB"),
            ("SQL syntax", "SELECT * FROM sales WHERE total_amount > 5000", "Oracle"),
            ("Cross-database analysis", "Compare user count in MongoDB with employee count in Oracle", None)
        ]
        
        for test_name, query, expected_db in routing_tests:
            await self.run_test(test_name, query, expected_db)
    
    async def run_advanced_tests(self):
        """Run advanced functionality tests."""
        print("\n" + "="*60)
        print("ADVANCED FUNCTIONALITY TESTS")
        print("="*60)
        
        advanced_tests = [
            ("MongoDB aggregation", "Show me the average rating of products by category", "MongoDB"),
            ("Oracle joins", "SELECT d.department_name, COUNT(e.employee_id) FROM departments d LEFT JOIN employees e ON d.department_id = e.department GROUP BY d.department_name", "Oracle"),
            ("MongoDB text search", "Find products with 'great' in the description", "MongoDB"),
            ("Oracle date functions", "SELECT * FROM sales WHERE sale_date >= TRUNC(SYSDATE, 'MM')", "Oracle"),
            ("MongoDB array operations", "Find users who have 'Python' in their skills array", "MongoDB"),
            ("Oracle subqueries", "SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)", "Oracle"),
            ("MongoDB indexing", "Create an index on the email field in the users collection", "MongoDB"),
            ("Oracle constraints", "Show me the constraints on the employees table", "Oracle"),
            ("MongoDB explain plan", "Explain the query plan for finding active users", "MongoDB"),
            ("Oracle performance", "Show me the execution plan for the sales by region query", "Oracle")
        ]
        
        for test_name, query, expected_db in advanced_tests:
            await self.run_test(test_name, query, expected_db)
    
    def print_summary(self):
        """Print test results summary."""
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result["success"])
        failed_tests = total_tests - successful_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {failed_tests}")
        print(f"Success Rate: {(successful_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ Failed Tests:")
            for result in self.test_results:
                if not result["success"]:
                    print(f"  - {result['test_name']}: {result['error']}")
        
        print("\n✅ Successful Tests:")
        for result in self.test_results:
            if result["success"]:
                print(f"  - {result['test_name']} ({result['response_length']} chars)")
        
        # Save detailed results
        with open("test_results.json", "w") as f:
            json.dump(self.test_results, f, indent=2, default=str)
        print(f"\n📄 Detailed results saved to test_results.json")
    
    async def run_all_tests(self):
        """Run all test suites."""
        print("🚀 Starting Multi-Database Agent Tests with Dummy Data")
        print("="*60)
        
        # Initialize agent
        if not await self.initialize_agent():
            return False
        
        # Run test suites
        await self.run_mongodb_tests()
        await self.run_oracle_tests()
        await self.run_intelligent_routing_tests()
        await self.run_advanced_tests()
        
        # Print summary
        self.print_summary()
        
        return True

async def main():
    """Main test function."""
    tester = AgentTester()
    success = await tester.run_all_tests()
    
    if success:
        print("\n🎉 All tests completed!")
        print("\nNext steps:")
        print("1. Check test_results.json for detailed results")
        print("2. Try the web UI: streamlit run chat_ui.py")
        print("3. Try the API: python api_server.py")
        print("4. Try the ADK CLI: adk web")
    else:
        print("\n⚠️  Tests failed. Check your configuration.")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
