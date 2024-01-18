from sqlalchemy import Index
from sqlalchemy.orm import Mapped, mapped_column
from pgvector.sqlalchemy import Vector
from app.db import BaseModel, DbHelper


class Embedding(BaseModel):
    text: Mapped[str]
    embedding: Mapped[Vector] = mapped_column(Vector(1536))


index = Index('embedding_index', Embedding.embedding,
              postgresql_using='hnsw',
              postgresql_with={'m': 16, 'ef_construction': 64},
              postgresql_ops={'embedding': 'vector_l2_ops'}
              )
