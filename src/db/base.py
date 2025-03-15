"""
This module contains the base database model.
For now, it's just a placeholder as we don't need actual database functionality.
"""

from sqlalchemy.orm import declarative_base

# Create base model
Base = declarative_base()


# Placeholder for future database session functionality
async def get_db():
    """
    Placeholder for database session.
    This will be implemented when database functionality is needed.
    """
    yield None
