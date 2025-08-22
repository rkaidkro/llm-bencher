"""
Conversations router for managing chat conversations and messages.

This module provides endpoints for creating, reading, updating, and deleting
conversations and their associated messages.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
import structlog

from ..models.database import get_db
from ..models.schemas import (
    ConversationCreate, ConversationUpdate, ConversationResponse,
    MessageCreate, MessageResponse,
    Conversation as ConversationModel, Message as MessageModel
)

# Configure logging
logger = structlog.get_logger()

router = APIRouter()


@router.get("/", response_model=List[ConversationResponse])
async def get_conversations(
    skip: int = Query(0, ge=0, description="Number of conversations to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of conversations to return"),
    search: Optional[str] = Query(None, description="Search term for conversation titles"),
    db: Session = Depends(get_db)
):
    """
    Get a list of conversations with optional pagination and search.
    
    Args:
        skip: Number of conversations to skip (for pagination)
        limit: Maximum number of conversations to return
        search: Optional search term for conversation titles
        db: Database session
        
    Returns:
        List of conversations with metadata
    """
    try:
        query = db.query(ConversationModel)
        
        # Apply search filter if provided
        if search:
            query = query.filter(ConversationModel.title.contains(search))
        
        # Apply pagination and ordering
        conversations = query.order_by(desc(ConversationModel.updated_at)).offset(skip).limit(limit).all()
        
        # Add message count to each conversation
        result = []
        for conv in conversations:
            message_count = db.query(MessageModel).filter(
                MessageModel.conversation_id == conv.id
            ).count()
            
            conv_response = ConversationResponse.from_orm(conv)
            conv_response.message_count = message_count
            result.append(conv_response)
        
        return result
        
    except Exception as e:
        logger.error(f"Failed to get conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversations")


@router.post("/", response_model=ConversationResponse)
async def create_conversation(
    conversation: ConversationCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new conversation.
    
    Args:
        conversation: Conversation data
        db: Database session
        
    Returns:
        Created conversation
    """
    try:
        db_conversation = ConversationModel(
            title=conversation.title or "New Conversation"
        )
        
        db.add(db_conversation)
        db.commit()
        db.refresh(db_conversation)
        
        logger.info(f"Created new conversation: {db_conversation.id}")
        
        return ConversationResponse.from_orm(db_conversation)
        
    except Exception as e:
        logger.error(f"Failed to create conversation: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific conversation by ID.
    
    Args:
        conversation_id: ID of the conversation
        db: Database session
        
    Returns:
        Conversation with metadata
    """
    try:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Add message count
        message_count = db.query(MessageModel).filter(
            MessageModel.conversation_id == conversation_id
        ).count()
        
        conv_response = ConversationResponse.from_orm(conversation)
        conv_response.message_count = message_count
        
        return conv_response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve conversation")


@router.put("/{conversation_id}", response_model=ConversationResponse)
async def update_conversation(
    conversation_id: int,
    conversation_update: ConversationUpdate,
    db: Session = Depends(get_db)
):
    """
    Update a conversation.
    
    Args:
        conversation_id: ID of the conversation to update
        conversation_update: Updated conversation data
        db: Database session
        
    Returns:
        Updated conversation
    """
    try:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Update fields if provided
        if conversation_update.title is not None:
            conversation.title = conversation_update.title
        
        db.commit()
        db.refresh(conversation)
        
        logger.info(f"Updated conversation: {conversation_id}")
        
        return ConversationResponse.from_orm(conversation)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update conversation {conversation_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update conversation")


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a conversation and all its messages.
    
    Args:
        conversation_id: ID of the conversation to delete
        db: Database session
        
    Returns:
        Success message
    """
    try:
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Delete conversation (messages will be deleted due to cascade)
        db.delete(conversation)
        db.commit()
        
        logger.info(f"Deleted conversation: {conversation_id}")
        
        return {"message": f"Conversation {conversation_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete conversation {conversation_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@router.get("/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: int,
    skip: int = Query(0, ge=0, description="Number of messages to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of messages to return"),
    db: Session = Depends(get_db)
):
    """
    Get messages for a specific conversation.
    
    Args:
        conversation_id: ID of the conversation
        skip: Number of messages to skip (for pagination)
        limit: Maximum number of messages to return
        db: Database session
        
    Returns:
        List of messages in the conversation
    """
    try:
        # Check if conversation exists
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Get messages with pagination
        messages = db.query(MessageModel).filter(
            MessageModel.conversation_id == conversation_id
        ).order_by(MessageModel.timestamp).offset(skip).limit(limit).all()
        
        return [MessageResponse.from_orm(msg) for msg in messages]
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get messages for conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve messages")


@router.post("/{conversation_id}/messages", response_model=MessageResponse)
async def create_message(
    conversation_id: int,
    message: MessageCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new message in a conversation.
    
    Args:
        conversation_id: ID of the conversation
        message: Message data
        db: Database session
        
    Returns:
        Created message
    """
    try:
        # Check if conversation exists
        conversation = db.query(ConversationModel).filter(
            ConversationModel.id == conversation_id
        ).first()
        
        if not conversation:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Create message
        db_message = MessageModel(
            conversation_id=conversation_id,
            role=message.role,
            content=message.content,
            model_used=message.model_used,
            response_time_ms=message.response_time_ms
        )
        
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        
        logger.info(f"Created message in conversation {conversation_id}")
        
        return MessageResponse.from_orm(db_message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create message in conversation {conversation_id}: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create message")


@router.get("/{conversation_id}/messages/{message_id}", response_model=MessageResponse)
async def get_message(
    conversation_id: int,
    message_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific message from a conversation.
    
    Args:
        conversation_id: ID of the conversation
        message_id: ID of the message
        db: Database session
        
    Returns:
        Message data
    """
    try:
        message = db.query(MessageModel).filter(
            MessageModel.id == message_id,
            MessageModel.conversation_id == conversation_id
        ).first()
        
        if not message:
            raise HTTPException(
                status_code=404,
                detail=f"Message {message_id} not found in conversation {conversation_id}"
            )
        
        return MessageResponse.from_orm(message)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get message {message_id} from conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve message")
