"""
LLM router for handling LLM-related API endpoints.

This module provides endpoints for generating responses from LLM services,
managing service configurations, and checking service health.
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import structlog

from ..models.database import get_db
from ..models.schemas import (
    LLMServiceCreate, LLMServiceUpdate, LLMServiceResponse,
    HealthCheckRequest, HealthCheckResponse
)
from ..services.llm_service import LLMService, LLMRequest, LLMResponse, LLMServiceError
from ..models.schemas import LLMService as LLMServiceModel, ServiceHealthLog

# Configure logging
logger = structlog.get_logger()

router = APIRouter()


@router.post("/generate", response_model=LLMResponse)
async def generate_response(
    request: LLMRequest,
    service_name: str = "ollama",
    db: Session = Depends(get_db)
):
    """
    Generate a response from an LLM service.
    
    Args:
        request: LLM request parameters
        service_name: Name of the LLM service to use
        db: Database session
        
    Returns:
        LLMResponse: Generated response with metadata
    """
    try:
        async with LLMService() as llm_service:
            response = await llm_service.generate_response(request, service_name)
            
            logger.info(
                "Generated LLM response",
                service=service_name,
                model=response.model_used,
                response_time_ms=response.response_time_ms,
                tokens_used=response.tokens_used
            )
            
            return response
            
    except LLMServiceError as e:
        logger.error(f"LLM service error: {e}")
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating response: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/services", response_model=List[LLMServiceResponse])
async def get_llm_services(db: Session = Depends(get_db)):
    """
    Get all configured LLM services.
    
    Args:
        db: Database session
        
    Returns:
        List of LLM service configurations
    """
    try:
        services = db.query(LLMServiceModel).all()
        return services
    except Exception as e:
        logger.error(f"Failed to get LLM services: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve services")


@router.post("/services", response_model=LLMServiceResponse)
async def create_llm_service(
    service: LLMServiceCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new LLM service configuration.
    
    Args:
        service: Service configuration data
        db: Database session
        
    Returns:
        Created LLM service configuration
    """
    try:
        # Check if service with same name already exists
        existing_service = db.query(LLMServiceModel).filter(
            LLMServiceModel.name == service.name
        ).first()
        
        if existing_service:
            raise HTTPException(
                status_code=400,
                detail=f"Service with name '{service.name}' already exists"
            )
        
        # Create new service
        db_service = LLMServiceModel(
            name=service.name,
            base_url=service.base_url,
            status="offline"  # Will be checked on first health check
        )
        
        db.add(db_service)
        db.commit()
        db.refresh(db_service)
        
        logger.info(f"Created new LLM service: {service.name}")
        return db_service
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create LLM service: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create service")


@router.put("/services/{service_id}", response_model=LLMServiceResponse)
async def update_llm_service(
    service_id: int,
    service_update: LLMServiceUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing LLM service configuration.
    
    Args:
        service_id: ID of the service to update
        service_update: Updated service data
        db: Database session
        
    Returns:
        Updated LLM service configuration
    """
    try:
        db_service = db.query(LLMServiceModel).filter(
            LLMServiceModel.id == service_id
        ).first()
        
        if not db_service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with ID {service_id} not found"
            )
        
        # Update fields if provided
        if service_update.name is not None:
            db_service.name = service_update.name
        if service_update.base_url is not None:
            db_service.base_url = service_update.base_url
        if service_update.status is not None:
            db_service.status = service_update.status
        
        db.commit()
        db.refresh(db_service)
        
        logger.info(f"Updated LLM service: {db_service.name}")
        return db_service
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update LLM service: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to update service")


@router.delete("/services/{service_id}")
async def delete_llm_service(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an LLM service configuration.
    
    Args:
        service_id: ID of the service to delete
        db: Database session
        
    Returns:
        Success message
    """
    try:
        db_service = db.query(LLMServiceModel).filter(
            LLMServiceModel.id == service_id
        ).first()
        
        if not db_service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with ID {service_id} not found"
            )
        
        service_name = db_service.name
        db.delete(db_service)
        db.commit()
        
        logger.info(f"Deleted LLM service: {service_name}")
        return {"message": f"Service '{service_name}' deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete LLM service: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to delete service")


@router.post("/services/{service_id}/health", response_model=HealthCheckResponse)
async def check_service_health(
    service_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Check the health of a specific LLM service.
    
    Args:
        service_id: ID of the service to check
        background_tasks: Background tasks for logging
        db: Database session
        
    Returns:
        Health check results
    """
    try:
        db_service = db.query(LLMServiceModel).filter(
            LLMServiceModel.id == service_id
        ).first()
        
        if not db_service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with ID {service_id} not found"
            )
        
        # Perform health check
        async with LLMService() as llm_service:
            health_result = await llm_service.check_service_health(db_service.name)
        
        # Update service status
        db_service.status = health_result["status"]
        db_service.last_checked = structlog.processors.TimeStamper(fmt="iso")()
        
        # Log health check result
        health_log = ServiceHealthLog(
            service_id=service_id,
            status=health_result["status"],
            response_time_ms=health_result.get("response_time_ms"),
            error_message=health_result.get("error")
        )
        
        db.add(health_log)
        db.commit()
        
        logger.info(
            f"Health check completed for service {db_service.name}",
            status=health_result["status"],
            response_time_ms=health_result.get("response_time_ms")
        )
        
        return HealthCheckResponse(
            service_id=service_id,
            status=health_result["status"],
            response_time_ms=health_result.get("response_time_ms"),
            error_message=health_result.get("error"),
            checked_at=health_log.checked_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check service health: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to check service health")


@router.get("/services/{service_id}/models")
async def get_service_models(
    service_id: int,
    db: Session = Depends(get_db)
):
    """
    Get available models for a specific LLM service.
    
    Args:
        service_id: ID of the service
        db: Database session
        
    Returns:
        List of available models
    """
    try:
        db_service = db.query(LLMServiceModel).filter(
            LLMServiceModel.id == service_id
        ).first()
        
        if not db_service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with ID {service_id} not found"
            )
        
        async with LLMService() as llm_service:
            models = await llm_service.get_available_models(db_service.name)
        
        return {"service": db_service.name, "models": models}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service models: {e}")
        raise HTTPException(status_code=500, detail="Failed to get models")
