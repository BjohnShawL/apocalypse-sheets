from flask_sqlalchemy import SQLAlchemy
from application.models.model import BaseModel

db = SQLAlchemy(model_class=BaseModel)