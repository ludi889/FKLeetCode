# app/db/base.py
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Import all models here so that anything importing `Base` gets the metadata populated
from app.models.problem import Problem, ProblemVariant
from app.models.session import Session