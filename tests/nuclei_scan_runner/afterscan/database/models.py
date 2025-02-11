from sqlalchemy import (
    JSON,
    TIMESTAMP,
    Boolean,
    Column,
    DateTime,
    ForeignKeyConstraint,
    Integer,
    String,
)

from nuclei_scan_runner.afterscan.database import get_base


class Finding(get_base()):
    __tablename__ = "findings"
    primary_key = Column(Integer, primary_key=True)
    finding_identifier = Column(String, nullable=False)
    name = Column(String, nullable=False)
    finding = Column(JSON, nullable=False)
    scan_id = Column(String, nullable=True)
    issue_id = Column(String, nullable=True)
    last_seen = Column(TIMESTAMP, nullable=True)
    severity = Column(String, nullable=True)


class Domains(get_base()):
    __tablename__ = "domains"
    name = Column(String, primary_key=True)
    port = Column(Integer, primary_key=True)
    discovered_tool = Column(String)
    discovered_time = Column(DateTime)
    last_seen = Column(DateTime)
    blacklisted = Column(Boolean)
    info = Column(String, nullable=True)


class Scanned(get_base()):
    # This table is used to store information about scans from different tools
    __tablename__ = "scan_info"
    name = Column(String, primary_key=True)
    port = Column(Integer, primary_key=True)
    scan_id = Column(String)
    timestamp = Column(DateTime, primary_key=True)
    info = Column(String, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(["name", "port"], ["domains.name", "domains.port"]),
    )
