#!/usr/bin/env python3
"""Script to create .env file manually"""

import os

# Create .env file content
env_content = """# MongoDB Connection Configuration
# Replace this with your actual MongoDB connection string from Atlas
MDB_MCP_CONNECTION_STRING=mongodb+srv://username:password@cluster.mongodb.net/database
"""

# Write to .env file
with open('.env', 'w') as f:
    f.write(env_content)

print("✅ Created .env file")
print("❌ IMPORTANT: Edit .env and replace with your actual MongoDB connection string!")
print("   Get it from: MongoDB Atlas → Clusters → Connect → Connect your application")
