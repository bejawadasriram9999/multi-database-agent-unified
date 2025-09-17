"""
Streamlit Chat UI for Multi-Database Agent
Provides a web-based interface for interacting with the multi-database agent.
"""

import streamlit as st
import os
import logging
from typing import List, Dict, Any
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Multi-Database Agent",
    page_icon="🗄️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .database-info {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .query-result {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .error-message {
        background-color: #ffe6e6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff4444;
        margin: 1rem 0;
    }
    .success-message {
        background-color: #e6ffe6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #44ff44;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

class ChatUI:
    """Streamlit-based chat interface for the multi-database agent."""
    
    def __init__(self):
        self.initialize_session_state()
        self.setup_sidebar()
    
    def initialize_session_state(self):
        """Initialize Streamlit session state variables."""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "agent_initialized" not in st.session_state:
            st.session_state.agent_initialized = False
        if "available_databases" not in st.session_state:
            st.session_state.available_databases = []
    
    def setup_sidebar(self):
        """Setup the sidebar with database information and controls."""
        with st.sidebar:
            st.title("🗄️ Database Info")
            
            # Database status
            st.subheader("Available Databases")
            
            # MongoDB status
            mongodb_connected = os.environ.get("MDB_MCP_CONNECTION_STRING") is not None
            st.write(f"**MongoDB (A & B):** {'✅ Connected' if mongodb_connected else '❌ Not configured'}")
            
            # Oracle status
            oracle_connected = os.environ.get("ORACLE_MCP_CONNECTION_STRING") is not None
            st.write(f"**Oracle (C):** {'✅ Connected' if oracle_connected else '❌ Not configured'}")
            
            st.divider()
            
            # Quick actions
            st.subheader("Quick Actions")
            if st.button("🔄 Refresh Connections"):
                st.rerun()
            
            if st.button("🗑️ Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
            
            st.divider()
            
            # Example queries
            st.subheader("Example Queries")
            example_queries = [
                "Show me all tables in Oracle database",
                "List collections in MongoDB",
                "Find documents in users collection",
                "SELECT * FROM employees WHERE department = 'IT'",
                "db.users.find({status: 'active'})"
            ]
            
            for query in example_queries:
                if st.button(f"💡 {query}", key=f"example_{query}"):
                    st.session_state.messages.append({
                        "role": "user",
                        "content": query,
                        "timestamp": datetime.now()
                    })
                    st.rerun()
            
            st.divider()
            
            # Database information
            st.subheader("Database Details")
            st.markdown("""
            **MongoDB (Databases A & B)**
            - Type: Document-based NoSQL
            - Query Language: MongoDB Query Language
            - Use Cases: Document storage, Real-time analytics
            
            **Oracle (Database C)**
            - Type: Relational SQL
            - Query Language: SQL
            - Use Cases: Transaction processing, Reporting
            """)
    
    def display_chat_messages(self):
        """Display chat messages in the main area."""
        st.markdown('<div class="main-header">Multi-Database Agent</div>', unsafe_allow_html=True)
        st.markdown("Ask questions about your MongoDB and Oracle databases. I'll help you query and analyze your data.")
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Show timestamp if available
                if "timestamp" in message:
                    st.caption(f"Sent at {message['timestamp'].strftime('%H:%M:%S')}")
                
                # Show database info if available
                if "database" in message:
                    st.info(f"Query executed on: {message['database']}")
                
                # Show query type if available
                if "query_type" in message:
                    st.caption(f"Query type: {message['query_type']}")
    
    def handle_user_input(self, user_input: str):
        """Handle user input and generate agent response."""
        if not user_input.strip():
            return
        
        # Add user message to chat
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        # Show loading spinner
        with st.spinner("Processing your query..."):
            try:
                # Import and initialize agent
                from mongodb_agent.agent import multi_db_agent
                
                # Get agent response
                agent = multi_db_agent.get_agent()
                response = agent.run(user_input)
                
                # Add agent response to chat
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": response,
                    "timestamp": datetime.now(),
                    "database": self._extract_database_from_response(response),
                    "query_type": self._extract_query_type(user_input)
                })
                
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                error_message = f"Sorry, I encountered an error processing your query: {str(e)}"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message,
                    "timestamp": datetime.now(),
                    "error": True
                })
    
    def _extract_database_from_response(self, response: str) -> str:
        """Extract database information from agent response."""
        response_lower = response.lower()
        if "mongodb" in response_lower or "mongo" in response_lower:
            return "MongoDB"
        elif "oracle" in response_lower:
            return "Oracle"
        else:
            return "Unknown"
    
    def _extract_query_type(self, query: str) -> str:
        """Extract query type from user input."""
        query_lower = query.lower()
        if any(word in query_lower for word in ['select', 'find', 'get', 'show', 'list']):
            return "Read"
        elif any(word in query_lower for word in ['insert', 'add', 'create']):
            return "Write"
        elif any(word in query_lower for word in ['update', 'modify', 'change']):
            return "Update"
        elif any(word in query_lower for word in ['delete', 'remove', 'drop']):
            return "Delete"
        else:
            return "Query"
    
    def run(self):
        """Run the chat UI."""
        self.display_chat_messages()
        
        # Chat input
        if prompt := st.chat_input("Ask about your databases..."):
            self.handle_user_input(prompt)
            st.rerun()
        
        # Display connection status
        if not st.session_state.agent_initialized:
            st.warning("⚠️ Please configure your database connections in the .env file to start using the agent.")
            
            with st.expander("Setup Instructions"):
                st.markdown("""
                ### Setup Instructions
                
                1. **Copy the example environment file:**
                   ```bash
                   cp example.env .env
                   ```
                
                2. **Configure your database connections:**
                   - Set `MDB_MCP_CONNECTION_STRING` for MongoDB
                   - Set `ORACLE_MCP_CONNECTION_STRING` for Oracle
                   - Set `GOOGLE_API_KEY` for Google ADK
                
                3. **Install dependencies:**
                   ```bash
                   pip install -r requirements.txt
                   ```
                
                4. **Start the agent:**
                   ```bash
                   adk web
                   ```
                """)

def main():
    """Main function to run the chat UI."""
    try:
        chat_ui = ChatUI()
        chat_ui.run()
    except Exception as e:
        st.error(f"Failed to initialize chat UI: {e}")
        logger.error(f"Chat UI initialization error: {e}")

if __name__ == "__main__":
    main()
