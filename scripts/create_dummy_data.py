#!/usr/bin/env python3
"""
Create Dummy Data for Multi-Database Agent Testing
This script creates dummy data in both MongoDB and Oracle databases for testing.
"""

import os
import sys
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_mongodb_dummy_data():
    """Create dummy data in MongoDB."""
    print("Creating MongoDB dummy data...")
    
    try:
        import pymongo
        from pymongo import MongoClient
        from bson import ObjectId
        
        # Connect to MongoDB
        connection_string = os.getenv("MDB_MCP_CONNECTION_STRING", "mongodb://localhost:27017/testdb")
        client = MongoClient(connection_string)
        
        # Test connection
        client.admin.command('ping')
        print("✅ Connected to MongoDB")
        
        # Create test database
        db = client['test_company_db']
        
        # Clear existing data
        db.users.drop()
        db.products.drop()
        db.orders.drop()
        db.analytics.drop()
        
        print("✅ Cleared existing test data")
        
        # Create dummy users
        users_data = []
        for i in range(50):
            user = {
                "_id": ObjectId(),
                "user_id": f"user_{i+1:03d}",
                "name": f"User {i+1}",
                "email": f"user{i+1}@example.com",
                "department": random.choice(["Engineering", "Sales", "Marketing", "HR", "Finance"]),
                "role": random.choice(["Manager", "Senior", "Junior", "Intern"]),
                "status": random.choice(["active", "inactive", "pending"]),
                "created_at": datetime.now() - timedelta(days=random.randint(1, 365)),
                "last_login": datetime.now() - timedelta(days=random.randint(0, 30)),
                "profile": {
                    "age": random.randint(22, 65),
                    "location": random.choice(["New York", "San Francisco", "London", "Tokyo", "Berlin"]),
                    "skills": random.sample(["Python", "JavaScript", "Java", "SQL", "MongoDB", "React", "Node.js"], k=random.randint(2, 5))
                }
            }
            users_data.append(user)
        
        db.users.insert_many(users_data)
        print(f"✅ Created {len(users_data)} users")
        
        # Create dummy products
        products_data = []
        categories = ["Electronics", "Clothing", "Books", "Home", "Sports", "Beauty"]
        for i in range(30):
            product = {
                "_id": ObjectId(),
                "product_id": f"prod_{i+1:03d}",
                "name": f"Product {i+1}",
                "category": random.choice(categories),
                "price": round(random.uniform(10, 1000), 2),
                "stock": random.randint(0, 100),
                "description": f"This is a great product {i+1}",
                "tags": random.sample(["popular", "new", "sale", "featured", "limited"], k=random.randint(1, 3)),
                "created_at": datetime.now() - timedelta(days=random.randint(1, 180)),
                "rating": round(random.uniform(3.0, 5.0), 1),
                "reviews_count": random.randint(0, 100)
            }
            products_data.append(product)
        
        db.products.insert_many(products_data)
        print(f"✅ Created {len(products_data)} products")
        
        # Create dummy orders
        orders_data = []
        for i in range(100):
            order = {
                "_id": ObjectId(),
                "order_id": f"order_{i+1:04d}",
                "user_id": f"user_{random.randint(1, 50):03d}",
                "products": [
                    {
                        "product_id": f"prod_{random.randint(1, 30):03d}",
                        "quantity": random.randint(1, 5),
                        "price": round(random.uniform(10, 500), 2)
                    }
                    for _ in range(random.randint(1, 3))
                ],
                "total_amount": round(random.uniform(50, 1000), 2),
                "status": random.choice(["pending", "processing", "shipped", "delivered", "cancelled"]),
                "order_date": datetime.now() - timedelta(days=random.randint(1, 90)),
                "shipping_address": {
                    "street": f"{random.randint(100, 999)} Main St",
                    "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix"]),
                    "state": random.choice(["NY", "CA", "IL", "TX", "AZ"]),
                    "zip": f"{random.randint(10000, 99999)}"
                }
            }
            orders_data.append(order)
        
        db.orders.insert_many(orders_data)
        print(f"✅ Created {len(orders_data)} orders")
        
        # Create dummy analytics data
        analytics_data = []
        for i in range(365):  # One year of data
            date = datetime.now() - timedelta(days=i)
            analytics = {
                "_id": ObjectId(),
                "date": date,
                "page_views": random.randint(1000, 10000),
                "unique_visitors": random.randint(500, 5000),
                "conversions": random.randint(10, 100),
                "revenue": round(random.uniform(1000, 10000), 2),
                "bounce_rate": round(random.uniform(0.2, 0.8), 3),
                "avg_session_duration": random.randint(60, 600),  # seconds
                "traffic_sources": {
                    "organic": random.randint(100, 1000),
                    "paid": random.randint(50, 500),
                    "social": random.randint(20, 200),
                    "direct": random.randint(100, 800)
                }
            }
            analytics_data.append(analytics)
        
        db.analytics.insert_many(analytics_data)
        print(f"✅ Created {len(analytics_data)} analytics records")
        
        # Create indexes for better performance
        db.users.create_index("email", unique=True)
        db.users.create_index("department")
        db.users.create_index("status")
        db.products.create_index("category")
        db.products.create_index("price")
        db.orders.create_index("user_id")
        db.orders.create_index("order_date")
        db.orders.create_index("status")
        db.analytics.create_index("date")
        
        print("✅ Created indexes for better performance")
        
        # Print summary
        print("\n📊 MongoDB Data Summary:")
        print(f"Users: {db.users.count_documents({})}")
        print(f"Products: {db.products.count_documents({})}")
        print(f"Orders: {db.orders.count_documents({})}")
        print(f"Analytics: {db.analytics.count_documents({})}")
        
        client.close()
        return True
        
    except ImportError:
        print("❌ pymongo not installed. Please install: pip install pymongo")
        return False
    except Exception as e:
        print(f"❌ Failed to create MongoDB dummy data: {e}")
        return False

def create_oracle_dummy_data():
    """Create dummy data in Oracle."""
    print("\nCreating Oracle dummy data...")
    
    try:
        import oracledb
        
        # Connect to Oracle
        connection_string = os.getenv("ORACLE_MCP_CONNECTION_STRING", "hr/hr@localhost:1521/XEPDB1")
        connection = oracledb.connect(connection_string)
        cursor = connection.cursor()
        
        print("✅ Connected to Oracle")
        
        # Create test schema and tables
        try:
            cursor.execute("CREATE USER test_company IDENTIFIED BY password")
            cursor.execute("GRANT CONNECT, RESOURCE TO test_company")
            cursor.execute("GRANT CREATE TABLE TO test_company")
            cursor.execute("GRANT CREATE SEQUENCE TO test_company")
            connection.commit()
            print("✅ Created test schema")
        except:
            print("ℹ️  Test schema already exists")
        
        # Connect to test schema
        cursor.close()
        connection.close()
        
        test_connection_string = connection_string.replace("hr/hr", "test_company/password")
        connection = oracledb.connect(test_connection_string)
        cursor = connection.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE employees (
                employee_id NUMBER PRIMARY KEY,
                first_name VARCHAR2(50),
                last_name VARCHAR2(50),
                email VARCHAR2(100),
                department VARCHAR2(50),
                job_title VARCHAR2(100),
                salary NUMBER(10,2),
                hire_date DATE,
                manager_id NUMBER,
                status VARCHAR2(20)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE departments (
                department_id NUMBER PRIMARY KEY,
                department_name VARCHAR2(50),
                manager_id NUMBER,
                location VARCHAR2(100),
                budget NUMBER(15,2)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE projects (
                project_id NUMBER PRIMARY KEY,
                project_name VARCHAR2(100),
                department_id NUMBER,
                start_date DATE,
                end_date DATE,
                budget NUMBER(15,2),
                status VARCHAR2(20)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE sales (
                sale_id NUMBER PRIMARY KEY,
                employee_id NUMBER,
                customer_name VARCHAR2(100),
                product_name VARCHAR2(100),
                quantity NUMBER,
                unit_price NUMBER(10,2),
                total_amount NUMBER(15,2),
                sale_date DATE,
                region VARCHAR2(50)
            )
        """)
        
        print("✅ Created tables")
        
        # Create sequences
        cursor.execute("CREATE SEQUENCE emp_seq START WITH 1 INCREMENT BY 1")
        cursor.execute("CREATE SEQUENCE dept_seq START WITH 1 INCREMENT BY 1")
        cursor.execute("CREATE SEQUENCE proj_seq START WITH 1 INCREMENT BY 1")
        cursor.execute("CREATE SEQUENCE sale_seq START WITH 1 INCREMENT BY 1")
        
        print("✅ Created sequences")
        
        # Insert departments
        departments = [
            ("Engineering", 1, "San Francisco", 2000000),
            ("Sales", 2, "New York", 1500000),
            ("Marketing", 3, "Los Angeles", 1000000),
            ("HR", 4, "Chicago", 500000),
            ("Finance", 5, "Boston", 800000)
        ]
        
        for dept_name, manager_id, location, budget in departments:
            cursor.execute("""
                INSERT INTO departments (department_id, department_name, manager_id, location, budget)
                VALUES (dept_seq.NEXTVAL, :1, :2, :3, :4)
            """, [dept_name, manager_id, location, budget])
        
        print("✅ Inserted departments")
        
        # Insert employees
        first_names = ["John", "Jane", "Mike", "Sarah", "David", "Lisa", "Tom", "Amy", "Chris", "Emma"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        job_titles = ["Software Engineer", "Senior Developer", "Product Manager", "Sales Rep", "Marketing Specialist", "HR Manager", "Financial Analyst", "Data Scientist", "DevOps Engineer", "UX Designer"]
        departments = ["Engineering", "Sales", "Marketing", "HR", "Finance"]
        
        for i in range(50):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            email = f"{first_name.lower()}.{last_name.lower()}@company.com"
            department = random.choice(departments)
            job_title = random.choice(job_titles)
            salary = random.randint(50000, 150000)
            hire_date = datetime.now() - timedelta(days=random.randint(30, 1095))
            manager_id = random.randint(1, 10) if i > 10 else None
            status = random.choice(["Active", "Inactive", "On Leave"])
            
            cursor.execute("""
                INSERT INTO employees (employee_id, first_name, last_name, email, department, job_title, salary, hire_date, manager_id, status)
                VALUES (emp_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8, :9)
            """, [first_name, last_name, email, department, job_title, salary, hire_date, manager_id, status])
        
        print("✅ Inserted employees")
        
        # Insert projects
        project_names = ["Website Redesign", "Mobile App", "Data Migration", "Security Audit", "Performance Optimization", "New Feature Development", "API Integration", "Database Upgrade", "Cloud Migration", "Analytics Dashboard"]
        
        for i in range(20):
            project_name = random.choice(project_names) + f" {i+1}"
            department_id = random.randint(1, 5)
            start_date = datetime.now() - timedelta(days=random.randint(30, 365))
            end_date = start_date + timedelta(days=random.randint(30, 180))
            budget = random.randint(50000, 500000)
            status = random.choice(["Planning", "In Progress", "Completed", "On Hold"])
            
            cursor.execute("""
                INSERT INTO projects (project_id, project_name, department_id, start_date, end_date, budget, status)
                VALUES (proj_seq.NEXTVAL, :1, :2, :3, :4, :5, :6)
            """, [project_name, department_id, start_date, end_date, budget, status])
        
        print("✅ Inserted projects")
        
        # Insert sales data
        customers = ["Acme Corp", "Tech Solutions", "Global Industries", "Startup Inc", "Enterprise Ltd", "Innovation Co", "Future Systems", "Digital Works", "Smart Solutions", "Next Gen Corp"]
        products = ["Software License", "Consulting", "Support Package", "Training", "Custom Development", "Integration", "Maintenance", "Upgrade", "Migration", "Optimization"]
        regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
        
        for i in range(100):
            employee_id = random.randint(1, 50)
            customer_name = random.choice(customers)
            product_name = random.choice(products)
            quantity = random.randint(1, 10)
            unit_price = random.randint(1000, 10000)
            total_amount = quantity * unit_price
            sale_date = datetime.now() - timedelta(days=random.randint(1, 365))
            region = random.choice(regions)
            
            cursor.execute("""
                INSERT INTO sales (sale_id, employee_id, customer_name, product_name, quantity, unit_price, total_amount, sale_date, region)
                VALUES (sale_seq.NEXTVAL, :1, :2, :3, :4, :5, :6, :7, :8)
            """, [employee_id, customer_name, product_name, quantity, unit_price, total_amount, sale_date, region])
        
        print("✅ Inserted sales data")
        
        # Create indexes
        cursor.execute("CREATE INDEX idx_emp_dept ON employees(department)")
        cursor.execute("CREATE INDEX idx_emp_status ON employees(status)")
        cursor.execute("CREATE INDEX idx_sales_date ON sales(sale_date)")
        cursor.execute("CREATE INDEX idx_sales_region ON sales(region)")
        
        print("✅ Created indexes")
        
        # Commit and close
        connection.commit()
        cursor.close()
        connection.close()
        
        print("\n📊 Oracle Data Summary:")
        print("Tables created: employees, departments, projects, sales")
        print("Records inserted: ~220 total")
        
        return True
        
    except ImportError:
        print("❌ oracledb not installed. Please install: pip install oracledb")
        return False
    except Exception as e:
        print(f"❌ Failed to create Oracle dummy data: {e}")
        return False

def main():
    """Main function to create dummy data."""
    print("=" * 60)
    print("Creating Dummy Data for Multi-Database Agent Testing")
    print("=" * 60)
    
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    success_count = 0
    total_tests = 2
    
    # Create MongoDB dummy data
    if create_mongodb_dummy_data():
        success_count += 1
    
    # Create Oracle dummy data
    if create_oracle_dummy_data():
        success_count += 1
    
    print("\n" + "=" * 60)
    print(f"Results: {success_count}/{total_tests} databases populated")
    
    if success_count == total_tests:
        print("🎉 All dummy data created successfully!")
        print("\nYou can now test the multi-database agent with:")
        print("1. python scripts/test_agent_with_dummy_data.py")
        print("2. streamlit run chat_ui.py")
        print("3. python api_server.py")
    else:
        print("⚠️  Some databases failed to populate. Check your connections.")
    
    return 0 if success_count == total_tests else 1

if __name__ == "__main__":
    sys.exit(main())
