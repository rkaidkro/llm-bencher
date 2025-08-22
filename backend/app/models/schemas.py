"""
Database models and schemas for the LLM Testing Interface.

This module defines the SQLAlchemy models for storing conversations,
messages, and LLM service configurations.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import List, Optional

from .database import Base


class Conversation(Base):
    """
    Model for storing conversation metadata.
    
    Each conversation represents a chat session with an LLM,
    containing multiple messages.
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, title='{self.title}', created_at={self.created_at})>"


class Message(Base):
    """
    Model for storing individual messages in conversations.
    
    Each message represents a single exchange (user input or LLM response)
    within a conversation.
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False, index=True)
    content = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    model_used = Column(String(100), nullable=True, index=True)
    response_time_ms = Column(Integer, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(role.in_(['user', 'assistant']), name='valid_role'),
    )
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(id={self.id}, role='{self.role}', conversation_id={self.conversation_id})>"


class LLMService(Base):
    """
    Model for storing LLM service configurations.
    
    Each service represents a different LLM provider or endpoint
    that can be used for generating responses.
    """
    __tablename__ = "llm_services"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    base_url = Column(String(500), nullable=False)
    status = Column(String(20), nullable=False, default="offline", index=True)
    last_checked = Column(DateTime(timezone=True), nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint(status.in_(['online', 'offline', 'error']), name='valid_status'),
    )
    
    def __repr__(self):
        return f"<LLMService(id={self.id}, name='{self.name}', status='{self.status}')>"


class ServiceHealthLog(Base):
    """
    Model for storing service health check logs.
    
    This table tracks the health status of LLM services over time,
    useful for monitoring and debugging.
    """
    __tablename__ = "service_health_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    service_id = Column(Integer, ForeignKey("llm_services.id"), nullable=False, index=True)
    status = Column(String(20), nullable=False, index=True)
    response_time_ms = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
    checked_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    # Relationships
    service = relationship("LLMService")
    
    def __repr__(self):
        return f"<ServiceHealthLog(id={self.id}, service_id={self.service_id}, status='{self.status}')>"


# Pydantic models for API requests/responses
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ConversationBase(BaseModel):
    """Base Pydantic model for conversation data."""
    title: Optional[str] = Field(None, max_length=255)


class ConversationCreate(ConversationBase):
    """Pydantic model for creating a new conversation."""
    pass


class ConversationUpdate(ConversationBase):
    """Pydantic model for updating a conversation."""
    title: Optional[str] = Field(None, max_length=255)


class ConversationResponse(ConversationBase):
    """Pydantic model for conversation responses."""
    id: int
    created_at: datetime
    updated_at: datetime
    message_count: int = 0
    
    class Config:
        from_attributes = True


class MessageBase(BaseModel):
    """Base Pydantic model for message data."""
    role: str = Field(..., pattern="^(user|assistant)$")
    content: str = Field(..., min_length=1)
    model_used: Optional[str] = Field(None, max_length=100)
    response_time_ms: Optional[int] = Field(None, ge=0)


class MessageCreate(MessageBase):
    """Pydantic model for creating a new message."""
    conversation_id: int


class MessageResponse(MessageBase):
    """Pydantic model for message responses."""
    id: int
    conversation_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True


class LLMServiceBase(BaseModel):
    """Base Pydantic model for LLM service data."""
    name: str = Field(..., max_length=100)
    base_url: str = Field(..., max_length=500)


class LLMServiceCreate(LLMServiceBase):
    """Pydantic model for creating a new LLM service."""
    pass


class LLMServiceUpdate(BaseModel):
    """Pydantic model for updating an LLM service."""
    name: Optional[str] = Field(None, max_length=100)
    base_url: Optional[str] = Field(None, max_length=500)
    status: Optional[str] = Field(None, pattern="^(online|offline|error)$")


class LLMServiceResponse(LLMServiceBase):
    """Pydantic model for LLM service responses."""
    id: int
    status: str
    last_checked: Optional[datetime]
    
    class Config:
        from_attributes = True


class HealthCheckRequest(BaseModel):
    """Pydantic model for health check requests."""
    service_id: int


class HealthCheckResponse(BaseModel):
    """Pydantic model for health check responses."""
    service_id: int
    status: str
    response_time_ms: Optional[int]
    error_message: Optional[str]
    checked_at: datetime
    
    class Config:
        from_attributes = True
