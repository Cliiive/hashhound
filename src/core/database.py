from sqlalchemy import create_engine, Column, Text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from pathlib import Path
import os
import sys

# Create base class for ORM models
Base = declarative_base()


class DatabaseConnection:
    """Database connection manager for SQLite databases"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.engine = None
        self.session_factory = None
    
    def connect(self):
        """Establish connection to the database"""
        try:
            # Validate database file exists
            if not os.path.exists(self.db_path):
                raise FileNotFoundError(f"Database file not found: {self.db_path}")
            
            # Create SQLAlchemy engine
            db_url = f"sqlite:///{self.db_path}"
            self.engine = create_engine(
                db_url,
                echo=False,  # Set to True for SQL debugging
                connect_args={"check_same_thread": False}  # For SQLite threading
            )
            
            # Create session factory
            self.session_factory = sessionmaker(bind=self.engine)
            
            return True
            
        except Exception as e:
            print(f"Error connecting to database: {e}", file=sys.stderr)
            return False
    
    def get_session(self) -> Session:
        """Get a new database session"""
        if not self.session_factory:
            raise RuntimeError("Database connection not established. Call connect() first.")
        
        return self.session_factory()
    
    def close(self):
        """Close database connection"""
        if self.engine:
            self.engine.dispose()


def open_database(db_path: str) -> DatabaseConnection:
    """
    Open a database file and return a DatabaseConnection object
    
    Args:
        db_path (str): Path to the SQLite database file
    
    Returns:
        DatabaseConnection: Database connection object with session access
        
    Raises:
        FileNotFoundError: If database file doesn't exist
        RuntimeError: If connection fails
    """
    # Validate input
    if not db_path:
        raise ValueError("Database path cannot be empty")
    
    # Convert to absolute path
    db_path = os.path.abspath(db_path)
    
    # Create database connection
    db_conn = DatabaseConnection(db_path)
    
    # Establish connection
    if not db_conn.connect():
        raise RuntimeError(f"Failed to connect to database: {db_path}")
    
    return db_conn


def create_database_session(db_path: str) -> Session:
    """
    Convenience function to directly get a database session
    
    Args:
        db_path (str): Path to the SQLite database file
    
    Returns:
        Session: SQLAlchemy session object
    """
    db_conn = open_database(db_path)
    return db_conn.get_session()

def get_hashes(session: Session) -> list:
    """Get all hashes from the VIC_HASHES table."""
    result = session.query(VicHashes).all()
    # contvert to list of hash values
    return [row.hash_value for row in result]

class VicHashes(Base):
    __tablename__ = 'VIC_HASHES'
    hash_value = Column(Text, primary_key=True)
