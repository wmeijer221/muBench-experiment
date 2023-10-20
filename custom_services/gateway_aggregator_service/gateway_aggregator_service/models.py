"""
Implements used data models.
"""

from pydantic import BaseModel

class Ratio(BaseModel):
    """It's a ratio"""
    ratio: float = 1

class Targets(BaseModel):
    """Data model for target service endpoints."""
    service_1: str
    service_2: str
    service_3: str
