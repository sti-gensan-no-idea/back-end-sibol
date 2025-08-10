"""
Database models import module
This ensures all models are imported and registered with SQLAlchemy Base
"""

# Import simplified models that work without complex relationships
from app.models.simple_models import *

# This way all models are available without relationship conflicts
