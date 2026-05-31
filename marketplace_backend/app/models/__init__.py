# This __init__.py is NOT empty — it serves two purposes:
#
# 1. CENTRALIZES IMPORTS: instead of importing each model individually
#    in every file, you can simply write:
#    'from app.models import Admin, Product, Order'
#
# 2. ALEMBIC DISCOVERY: when Alembic generates migrations, it needs
#    to "see" all models. By importing them all here, a single
#    'import app.models' is enough for Alembic to find every table
#    and generate the correct migration scripts.


from app.models.base import Base
from app.models.admin import Admin
from app.models.categories import Categories
from app.models.products import Product
from app.models.product_variants import ProductVariants
