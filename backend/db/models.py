from sqlalchemy import Column, String, Integer, Text, DateTime, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.sql import expression
from sqlalchemy.event import listens_for
from sqlalchemy.ext.compiler import compiles
from db.database import Base

class Resource(Base):
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    subject = Column(String, nullable=False)
    semester = Column(String, nullable=False)
    department = Column(String, nullable=False)
    type = Column(String, nullable=False)
    source = Column(String, nullable=False)  # "github" or "drive"
    link = Column(Text, nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # PostgreSQL full-text search column
    search_vector = Column(TSVECTOR)

# Auto-generate tsvector on insert/update using a DB trigger (optional)
@listens_for(Resource, 'after_insert')
@listens_for(Resource, 'after_update')
def update_search_vector(mapper, connection, target):
    connection.execute(
        Resource.__table__.update()
        .where(Resource.id == target.id)
        .values(
            search_vector=func.to_tsvector('english', f"{target.title} {target.subject} {target.semester} {target.department}")
        )
    )
