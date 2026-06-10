from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime,
    ForeignKey, UniqueConstraint, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

BaseApp = declarative_base()

class ServerSettings(BaseApp):
    __tablename__ = "server_settings"

    uuid = Column(
        String, 
        primary_key=True, 
        default=lambda: str(uuid.uuid4())
    )
    owner_id = Column(String, nullable=False)
    guild_id = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    embed_id = Column(String, nullable=False)
    api_token = Column(String, nullable=True)
    server_ip = Column(String, nullable=False)
    server_port = Column(String, nullable=False)
    client_password = Column(String, nullable=True)
    container_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    privileges = relationship(
        "ServerControlPrivilege",
        back_populates="server",
        cascade="all, delete-orphan"
    )


class ServerControlPrivilege(BaseApp):
    __tablename__ = "server_control_privilege"

    id = Column(Integer, primary_key=True)
    server_uuid = Column(
        String, 
        ForeignKey("server_settings.uuid", ondelete="CASCADE"),
        nullable=False
    )
    guild_id = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    principal_id = Column(String, nullable=False)
    principal_name = Column(String, nullable=False)
    privilege_type = Column(String, nullable=False)
    control_start = Column(Boolean, default=False, nullable=False)
    control_stop = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    server = relationship("ServerSettings", back_populates="privileges")

    __table_args__ = (
        UniqueConstraint(
            "server_uuid", "privilege_type", "principal_id",
            name="uq_privilege_per_principal"
        ),
        Index("ix_priv_principal", "privilege_type", "principal_id"),
    )