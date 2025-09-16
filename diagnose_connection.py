#!/usr/bin/env python3
"""Comprehensive diagnostic script for MongoDB MCP connection issues"""

import os
import subprocess
import sys
from dotenv import load_dotenv

def run_command(cmd, description):
    """Run a command and return the result"""
    print(f"\n🔍 {description}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            print("✅ Success"            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print("❌ Failed"            if result.stderr.strip():
                print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("⏰ Timeout (30s)")
        return False
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("="*60)
    print("MongoDB MCP Connection Diagnostic")
    print("="*60)

    # 1. Check .env file
    print("\n1. Checking .env file...")
    if os.path.exists('.env'):
        print("✅ .env file exists")
        try:
            with open('.env', 'r') as f:
                content = f.read().strip()
                if content:
                    lines = content.split('\n')
                    print(f"   Contains {len(lines)} lines")
                    for i, line in enumerate(lines):
                        if line.strip() and not line.startswith('#'):
                            key = line.split('=')[0] if '=' in line else line
                            print(f"   Line {i+1}: {key}=***")
                        else:
                            print(f"   Line {i+1}: {line[:50]}...")
                else:
                    print("❌ .env file is empty")
        except Exception as e:
            print(f"❌ Error reading .env: {e}")
    else:
        print("❌ .env file not found")

    # 2. Load environment variables
    print("\n2. Loading environment variables...")
    load_dotenv()
    connection_string = os.getenv("MDB_MCP_CONNECTION_STRING")
    if connection_string:
        print("✅ MDB_MCP_CONNECTION_STRING found")
        masked = connection_string.replace(connection_string.split('@')[0] if '@' in connection_string else connection_string, "***")
        print(f"   Connection: {masked}")
    else:
        print("❌ MDB_MCP_CONNECTION_STRING not found")

    # 3. Test basic npx
    print("\n3. Testing npx command...")
    run_command("npx --version", "Checking npx availability")

    # 4. Test MongoDB MCP server directly
    print("\n4. Testing MongoDB MCP server startup...")
    if connection_string:
        # Test with a timeout to avoid hanging
        cmd = f'npx mongodb-mcp-server@latest --help'
        run_command(cmd, "Testing MCP server help command")
    else:
        print("⚠️ Skipping MCP server test (no connection string)")

    # 5. Test network connectivity (if connection string has a host)
    if connection_string and '@' in connection_string:
        try:
            host_part = connection_string.split('@')[1].split('/')[0]
            host = host_part.split(':')[0]
            print(f"\n5. Testing network connectivity to {host}...")
            run_command(f"ping -n 2 {host}", f"Testing ping to {host}")
        except:
            print("⚠️ Could not extract host from connection string")

    print("\n" + "="*60)
    print("DIAGNOSTIC COMPLETE")
    print("="*60)
    print("\nNext steps:")
    print("1. Create/edit .env file with your MongoDB connection string")
    print("2. Ensure your MongoDB cluster allows connections from your IP")
    print("3. Check your connection string format")
    print("4. Try: adk web")

if __name__ == "__main__":
    main()
