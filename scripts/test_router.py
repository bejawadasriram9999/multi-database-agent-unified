#!/usr/bin/env python3
"""
Test Database Router
This script tests the intelligent database routing functionality.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database_router import database_router

def test_database_router():
    """Test the database router with various queries."""
    print('🧪 Testing Database Router with Sample Queries')
    print('=' * 60)

    test_queries = [
        'Show me all users in the Engineering department',
        'SELECT * FROM employees WHERE department = "Engineering"',
        'Find all active users',
        'db.users.find({status: "active"})',
        'Get employee count by department',
        'Query database A for all users',
        'Query database C for all employees',
        'Show me all tables in the database',
        'List all collections in MongoDB',
        'Find products with price between 100 and 500',
        'Create an index on the email field',
        'INSERT INTO employees VALUES (...)',
        'db.products.aggregate([{$group: {_id: "$category", count: {$sum: 1}}}])',
        'UPDATE employees SET salary = 75000 WHERE department = "Engineering"',
        'Find users who have Python in their skills array'
    ]

    for i, query in enumerate(test_queries, 1):
        db_type, confidence, reasoning = database_router.route_query(query)
        print(f'{i:2d}. Query: {query}')
        print(f'    Database: {db_type.value} (Confidence: {confidence:.2f})')
        print(f'    Reasoning: {reasoning}')
        print('-' * 60)

def test_query_types():
    """Test query type detection."""
    print('\n🔍 Testing Query Type Detection')
    print('=' * 60)

    test_queries = [
        'SELECT * FROM employees',
        'INSERT INTO users VALUES (...)',
        'UPDATE employees SET salary = 75000',
        'DELETE FROM users WHERE status = "inactive"',
        'CREATE TABLE new_table (...)',
        'DROP TABLE old_table',
        'EXPLAIN SELECT * FROM employees',
        'ANALYZE TABLE employees'
    ]

    for query in test_queries:
        query_type = database_router.get_query_type(query)
        is_write = database_router.is_write_operation(query)
        print(f'Query: {query}')
        print(f'Type: {query_type.value}')
        print(f'Write Operation: {is_write}')
        print('-' * 40)

def test_database_info():
    """Test database information retrieval."""
    print('\n📊 Database Information')
    print('=' * 60)

    db_info = database_router.get_database_info()
    
    for db_name, info in db_info.items():
        print(f'{db_name}:')
        print(f'  Databases: {", ".join(info["databases"])}')
        print(f'  Type: {info["type"]}')
        print(f'  Query Language: {info["query_language"]}')
        print(f'  Use Cases: {", ".join(info["use_cases"])}')
        print()

def main():
    """Main test function."""
    test_database_router()
    test_query_types()
    test_database_info()
    
    print('\n🎉 Database Router Tests Complete!')
    print('The router successfully analyzes queries and determines the appropriate database.')

if __name__ == "__main__":
    main()
