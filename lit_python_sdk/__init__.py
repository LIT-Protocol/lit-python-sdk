from .client import LitClient

__version__ = "0.1.0"

def connect():
    """Creates and returns a new LitClient instance"""
    return LitClient() 