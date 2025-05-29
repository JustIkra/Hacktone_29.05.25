from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from app.database import Base
import enum, datetime

class UserRole(enum.Enum):
    portal_admin = "portal_admin"
    client_admin = "client_admin"
    user = "user"

class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    tariff = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    users = relationship("User", back_populates="client")
    client_services = relationship("ClientService", back_populates="client")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=True)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.user)
    client_id = Column(Integer, ForeignKey("clients.id"))
    client = relationship("Client", back_populates="users")

class Service(Base):
    __tablename__ = "services"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

class ClientService(Base):
    __tablename__ = "client_services"
    id = Column(Integer, primary_key=True)
    client_id = Column(Integer, ForeignKey("clients.id"))
    service_id = Column(Integer, ForeignKey("services.id"))
    connected_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    client = relationship("Client", back_populates="client_services")
    service = relationship("Service")

class Usage(Base):
    __tablename__ = "usage"
    id = Column(Integer, primary_key=True)
    client_service_id = Column(Integer, ForeignKey("client_services.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    usage_date = Column(DateTime, default=datetime.datetime.utcnow)
    usage_amount = Column(Integer)
