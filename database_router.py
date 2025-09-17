"""
Database Router for Multi-Database Agent
Determines which database to query based on user input and query patterns.
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from enum import Enum

logger = logging.getLogger(__name__)

class DatabaseType(Enum):
    """Supported database types."""
    MONGODB = "mongodb"
    ORACLE = "oracle"
    UNKNOWN = "unknown"

class QueryType(Enum):
    """Query operation types."""
    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    CREATE = "create"
    DROP = "drop"
    ANALYZE = "analyze"
    EXPLAIN = "explain"

class DatabaseRouter:
    """
    Routes user queries to appropriate databases based on content analysis.
    """
    
    def __init__(self):
        # MongoDB-specific keywords and patterns
        self.mongodb_keywords = {
            'collections', 'documents', 'bson', 'aggregation', 'pipeline',
            'find', 'findone', 'insertone', 'insertmany', 'updateone',
            'updatemany', 'deleteone', 'deletemany', 'count', 'distinct',
            'index', 'indexes', 'shard', 'replica', 'mongodb', 'mongo',
            'nosql', 'document', 'collection', 'db.collection', 'db.',
            'lookup', 'match', 'group', 'sort', 'limit', 'skip', 'project'
        }
        
        # Oracle-specific keywords and patterns
        self.oracle_keywords = {
            'table', 'tables', 'schema', 'schemas', 'view', 'views',
            'procedure', 'procedures', 'function', 'functions', 'trigger',
            'triggers', 'sequence', 'sequences', 'index', 'indexes',
            'constraint', 'constraints', 'primary key', 'foreign key',
            'unique', 'check', 'oracle', 'sql', 'select', 'insert',
            'update', 'delete', 'create', 'alter', 'drop', 'grant',
            'revoke', 'commit', 'rollback', 'transaction', 'cursor',
            'pl/sql', 'plsql', 'package', 'packages'
        }
        
        # SQL patterns
        self.sql_patterns = [
            r'\bSELECT\b.*\bFROM\b',
            r'\bINSERT\s+INTO\b',
            r'\bUPDATE\b.*\bSET\b',
            r'\bDELETE\s+FROM\b',
            r'\bCREATE\s+TABLE\b',
            r'\bALTER\s+TABLE\b',
            r'\bDROP\s+TABLE\b',
            r'\bCREATE\s+INDEX\b',
            r'\bGRANT\b',
            r'\bREVOKE\b'
        ]
        
        # MongoDB patterns
        self.mongodb_patterns = [
            r'db\.\w+\.',
            r'\.find\(',
            r'\.aggregate\(',
            r'\.insertOne\(',
            r'\.insertMany\(',
            r'\.updateOne\(',
            r'\.updateMany\(',
            r'\.deleteOne\(',
            r'\.deleteMany\(',
            r'\$match',
            r'\$group',
            r'\$lookup',
            r'\$project',
            r'\$sort',
            r'\$limit',
            r'\$skip'
        ]
        
        # Database identifiers (A, B, C)
        self.database_identifiers = {
            'database a': DatabaseType.MONGODB,
            'database b': DatabaseType.MONGODB,
            'database c': DatabaseType.ORACLE,
            'db a': DatabaseType.MONGODB,
            'db b': DatabaseType.MONGODB,
            'db c': DatabaseType.ORACLE,
            'mongodb a': DatabaseType.MONGODB,
            'mongodb b': DatabaseType.MONGODB,
            'oracle c': DatabaseType.ORACLE
        }
    
    def route_query(self, user_query: str) -> Tuple[DatabaseType, float, str]:
        """
        Route a user query to the appropriate database.
        
        Args:
            user_query: The user's query string
            
        Returns:
            Tuple of (database_type, confidence_score, reasoning)
        """
        user_query_lower = user_query.lower()
        
        # Check for explicit database mentions first
        explicit_db = self._check_explicit_database_mention(user_query_lower)
        if explicit_db:
            return explicit_db, 1.0, "Explicit database mention detected"
        
        # Check for SQL patterns
        sql_score = self._calculate_sql_score(user_query)
        if sql_score > 0.5:
            return DatabaseType.ORACLE, sql_score, "SQL patterns detected"
        
        # Check for MongoDB patterns
        mongodb_score = self._calculate_mongodb_score(user_query)
        if mongodb_score > 0.5:
            return DatabaseType.MONGODB, mongodb_score, "MongoDB patterns detected"
        
        # Check for keyword matches
        oracle_keyword_score = self._calculate_keyword_score(user_query_lower, self.oracle_keywords)
        mongodb_keyword_score = self._calculate_keyword_score(user_query_lower, self.mongodb_keywords)
        
        if oracle_keyword_score > mongodb_keyword_score and oracle_keyword_score > 0.3:
            return DatabaseType.ORACLE, oracle_keyword_score, "Oracle keywords detected"
        elif mongodb_keyword_score > 0.3:
            return DatabaseType.MONGODB, mongodb_keyword_score, "MongoDB keywords detected"
        
        # Default to unknown if no clear pattern
        return DatabaseType.UNKNOWN, 0.0, "No clear database pattern detected"
    
    def _check_explicit_database_mention(self, query: str) -> Optional[DatabaseType]:
        """Check for explicit database mentions."""
        for identifier, db_type in self.database_identifiers.items():
            if identifier in query:
                return db_type
        return None
    
    def _calculate_sql_score(self, query: str) -> float:
        """Calculate confidence score for SQL patterns."""
        score = 0.0
        for pattern in self.sql_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 0.2
        return min(score, 1.0)
    
    def _calculate_mongodb_score(self, query: str) -> float:
        """Calculate confidence score for MongoDB patterns."""
        score = 0.0
        for pattern in self.mongodb_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                score += 0.2
        return min(score, 1.0)
    
    def _calculate_keyword_score(self, query: str, keywords: set) -> float:
        """Calculate confidence score based on keyword matches."""
        matches = 0
        total_words = len(query.split())
        
        for keyword in keywords:
            if keyword in query:
                matches += 1
        
        if total_words == 0:
            return 0.0
        
        return min(matches / total_words * 2, 1.0)  # Scale up and cap at 1.0
    
    def get_query_type(self, query: str) -> QueryType:
        """Determine the type of query operation."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['select', 'find', 'get', 'show', 'list', 'describe']):
            return QueryType.SELECT
        elif any(word in query_lower for word in ['insert', 'add', 'create document']):
            return QueryType.INSERT
        elif any(word in query_lower for word in ['update', 'modify', 'change']):
            return QueryType.UPDATE
        elif any(word in query_lower for word in ['delete', 'remove', 'drop document']):
            return QueryType.DELETE
        elif any(word in query_lower for word in ['create table', 'create collection']):
            return QueryType.CREATE
        elif any(word in query_lower for word in ['drop table', 'drop collection']):
            return QueryType.DROP
        elif any(word in query_lower for word in ['analyze', 'explain', 'performance']):
            return QueryType.ANALYZE
        else:
            return QueryType.SELECT  # Default to read operation
    
    def is_write_operation(self, query: str) -> bool:
        """Check if the query is a write operation."""
        write_keywords = [
            'insert', 'update', 'delete', 'create', 'drop', 'alter',
            'grant', 'revoke', 'commit', 'rollback'
        ]
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in write_keywords)
    
    def suggest_database_clarification(self, query: str) -> str:
        """Suggest clarification when database type is ambiguous."""
        suggestions = []
        
        if self._calculate_sql_score(query) > 0.3:
            suggestions.append("This looks like a SQL query - should I query the Oracle database (Database C)?")
        
        if self._calculate_mongodb_score(query) > 0.3:
            suggestions.append("This looks like a MongoDB query - should I query MongoDB (Database A or B)?")
        
        if not suggestions:
            suggestions.append("I'm not sure which database to query. Please specify:")
            suggestions.append("- 'MongoDB' or 'Database A/B' for document queries")
            suggestions.append("- 'Oracle' or 'Database C' for SQL queries")
        
        return " ".join(suggestions)
    
    def get_database_info(self) -> Dict[str, Dict]:
        """Get information about available databases."""
        return {
            "MongoDB": {
                "databases": ["Database A", "Database B"],
                "type": "Document-based NoSQL",
                "query_language": "MongoDB Query Language",
                "use_cases": ["Document storage", "Real-time analytics", "Content management"]
            },
            "Oracle": {
                "databases": ["Database C"],
                "type": "Relational SQL",
                "query_language": "SQL",
                "use_cases": ["Transaction processing", "Reporting", "Data warehousing"]
            }
        }

# Global router instance
database_router = DatabaseRouter()
