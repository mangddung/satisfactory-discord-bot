from sqlalchemy import (
    Table, Column, Integer, String, Boolean, DateTime,
    ForeignKey, UniqueConstraint
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

    member_privileges = relationship(
        "ServerControlPrivilegeMember",
        back_populates="server",
        cascade="all, delete-orphan"
    )
    role_privileges = relationship(
        "ServerControlPrivilegeRole",
        back_populates="server",
        cascade="all, delete-orphan"
    )


class ServerControlPrivilegeMember(BaseApp):
    __tablename__ = "server_control_privilege_member"

    id = Column(Integer, primary_key=True)
    server_uuid = Column(
        String, 
        ForeignKey("server_settings.uuid", ondelete="CASCADE"),
        nullable=False
    )
    guild_id = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    member_id = Column(String, nullable=False)
    member_name = Column(String, nullable=False)
    control_start = Column(Boolean, default=False, nullable=False)
    control_stop = Column(Boolean, default=False, nullable=False)
    control_restart = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    server = relationship("ServerSettings", back_populates="member_privileges")

    __table_args__ = (
        UniqueConstraint("server_uuid", "member_id", name="uq_member_privilege"),
    )


class ServerControlPrivilegeRole(BaseApp):
    __tablename__ = "server_control_privilege_role"

    id = Column(Integer, primary_key=True)
    server_uuid = Column(
        String, 
        ForeignKey("server_settings.uuid", ondelete="CASCADE"),
        nullable=False
    )
    guild_id = Column(String, nullable=False)
    channel_id = Column(String, nullable=False)
    role_id = Column(String, nullable=False)
    role_name = Column(String, nullable=False)
    control_start = Column(Boolean, default=False, nullable=False)
    control_stop = Column(Boolean, default=False, nullable=False)
    control_restart = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    server = relationship("ServerSettings", back_populates="role_privileges")

    __table_args__ = (
        UniqueConstraint("server_uuid", "role_id", name="uq_role_privilege"),
    )
