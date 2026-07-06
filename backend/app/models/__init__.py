# app/models/__init__.py

from app.models.problem import Problem, ProblemVariant
from app.models.session import Session

# Now, anytime Python looks at the `app.models` folder, 
# it automatically loads all three of these into memory!