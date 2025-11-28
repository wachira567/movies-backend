#1 import the necessary packages
# from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from sqlalchemy import Column, Integer, Text, DateTime
from sqlalchemy.orm import declarative_base # latest version

# 2. Setup the base class from which all our models will inherit from
Base = declarative_base()

# Data Integrity (Correctness) - db constraints NOT NULL, UNIQUE

# 3. Start creating the schema
class Genre(Base):
    # we must the table name via the attribute __tablename__
    __tablename__ = "genre"

    # it must have at least one column
    id = Column(Integer(), primary_key=True)
    name = Column(Text(), nullable=False, unique=True)
    created_at = Column(DateTime, default = datetime.now())
