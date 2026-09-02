"""Run model — iterative workspace for requirements validation and generation."""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.session import Base


class Run(Base):
    """Iterative workspace: edit requirements, validate, generate diagram."""
    __tablename__ = "runs"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    # Diagram type: "class" or "use_case"
    diagram_type = Column(String(20), default="class", nullable=False)
    # Detail level: "domain" (no methods/visibility) or "design" (with methods/visibility)
    detail_level = Column(String(20), default="domain", nullable=False)

    # Requirements (editable)
    requirements_text = Column(Text, default="")
    requirements_updated_at = Column(DateTime(timezone=True), nullable=True)

    # Validation (latest result)
    validation_status = Column(String(20), nullable=True)  # None | running | succeeded | failed
    validation_score = Column(Integer, nullable=True)  # 0-100
    validation_result = Column(JSON, nullable=True)  # Full validation JSON
    validated_at = Column(DateTime(timezone=True), nullable=True)

    # Generation (latest result)
    generation_status = Column(String(20), nullable=True)  # None | running | succeeded | failed
    diagram_data = Column(JSON, nullable=True)  # {plantuml_source, entities, relationships, ...}
    generated_at = Column(DateTime(timezone=True), nullable=True)

    # Performance metrics
    validation_time_ms = Column(Integer, nullable=True)
    generation_time_ms = Column(Integer, nullable=True)
    refine_iterations = Column(Integer, nullable=True, default=0)
    syntax_valid = Column(Boolean, nullable=True)
    llm_calls_count = Column(Integer, nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="runs")
    user = relationship("User", backref="runs")
    artifacts = relationship(
        "Artifact",
        back_populates="run",
        cascade="all, delete-orphan"
    )
