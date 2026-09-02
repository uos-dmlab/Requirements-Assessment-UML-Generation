"""Artifact model for storing generated files (diagrams, etc.)."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, LargeBinary
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Artifact(Base):
    """Generated artifact (diagram image, PlantUML file, etc.)."""
    __tablename__ = "artifacts"

    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(
        Integer,
        ForeignKey("runs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    kind = Column(String(50), nullable=False)  # uml_png, uml_svg, plantuml, etc.
    content_type = Column(String(100), nullable=False)  # image/png, text/plain, etc.
    filename = Column(String(255), nullable=True)

    # Store binary data directly (for small artifacts)
    # For larger files, use storage_path to external storage
    data = Column(LargeBinary, nullable=True)
    storage_path = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    run = relationship("Run", back_populates="artifacts")
    project = relationship("Project", backref="artifacts")
    user = relationship("User", backref="artifacts")
