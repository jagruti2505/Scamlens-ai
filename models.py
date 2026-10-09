from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    ForeignKey,
    JSON
)
from sqlalchemy.orm import relationship
from .database import Base


class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_type = Column(String(50), nullable=False, index=True)  # message, url, profile, recruiter, company, document
    input_summary = Column(String(500), nullable=False)
    status = Column(String(50), nullable=False, default="completed")
    risk_score = Column(Integer, nullable=False, default=0)
    risk_label = Column(String(50), nullable=False, index=True)
    scoring_method = Column(String(100), nullable=False, default="Deterministic Weighted Rule Engine v1.0")
    sources_checked = Column(JSON, nullable=True)
    unavailable_checks = Column(JSON, nullable=True)
    limitations = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    findings = relationship("Finding", back_populates="scan", cascade="all, delete-orphan")
    reports = relationship("Report", back_populates="scan", cascade="all, delete-orphan")


class Finding(Base):
    __tablename__ = "findings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    indicator = Column(String(255), nullable=False)
    severity = Column(String(50), nullable=False)  # critical, high, medium, low, info
    strength = Column(String(50), nullable=False)  # high, moderate, low
    evidence = Column(Text, nullable=True)
    explanation = Column(Text, nullable=False)

    # Relationship
    scan = relationship("Scan", back_populates="findings")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    scan_id = Column(Integer, ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(50), nullable=False, default="comprehensive_audit")
    report_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    scan = relationship("Scan", back_populates="reports")
