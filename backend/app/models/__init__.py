"""
models/__init__.py - Models Package

This file makes the "models" folder a Python package and imports all models.
When Python sees an __init__.py file in a folder, it treats that folder
as a package that can be imported.

We import all models here so that when the app starts, SQLAlchemy knows
about all the tables it needs to create.
"""

from app.models.user import User
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.delivery import Delivery
