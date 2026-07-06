# app/db/base.py

# 1. Import the Base from the new file
from app.db.base_class import Base

# 2. Import all models here so Alembic can see them attached to Base
from app.models.problem import Problem, ProblemVariant
from app.models.session import Session