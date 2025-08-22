"""
Monitoring router for system health, logs, and performance monitoring.

This module provides endpoints for monitoring system health, viewing logs,
and tracking performance metrics.
"""

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import structlog

from ..models.database import get_db
from ..models.schemas import (
    LLMService as LLMServiceModel, ServiceHealthLog
)
from ..services.llm_service import LLMService

# Configure logging
logger = structlog.get_logger()

router = APIRouter()


@router.get("/health")
async def get_system_health():
    """
    Get overall system health status.
    
    Returns:
        System health information
    """
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "1.0.0",
            "uptime": "running"  # TODO: Add actual uptime tracking
        }
    except Exception as e:
        logger.error(f"Failed to get system health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system health")


@router.get("/health/services")
async def get_services_health():
    """
    Get health status of all LLM services.
    
    Returns:
        Health status of all configured services
    """
    try:
        services = ["ollama", "lm_studio"]
        results = {}
        
        async with LLMService() as llm_service:
            for service in services:
                try:
                    health = await llm_service.check_service_health(service)
                    results[service] = health
                except Exception as e:
                    logger.error(f"Health check failed for {service}: {e}")
                    results[service] = {
                        "status": "error",
                        "error": str(e),
                        "response_time_ms": 0
                    }
        
        return {
            "services": results,
            "timestamp": datetime.utcnow().isoformat(),
            "overall_status": "healthy" if all(
                s.get("status") == "online" for s in results.values()
            ) else "degraded"
        }
        
    except Exception as e:
        logger.error(f"Failed to get services health: {e}")
        raise HTTPException(status_code=500, detail="Failed to get services health")


@router.get("/health/services/{service_id}")
async def get_service_health_history(
    service_id: int,
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    db: Session = Depends(get_db)
):
    """
    Get health check history for a specific service.
    
    Args:
        service_id: ID of the service
        hours: Number of hours to look back
        db: Database session
        
    Returns:
        Health check history for the service
    """
    try:
        # Check if service exists
        service = db.query(LLMServiceModel).filter(
            LLMServiceModel.id == service_id
        ).first()
        
        if not service:
            raise HTTPException(
                status_code=404,
                detail=f"Service with ID {service_id} not found"
            )
        
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get health logs within time range
        health_logs = db.query(ServiceHealthLog).filter(
            ServiceHealthLog.service_id == service_id,
            ServiceHealthLog.checked_at >= start_time,
            ServiceHealthLog.checked_at <= end_time
        ).order_by(desc(ServiceHealthLog.checked_at)).all()
        
        # Calculate statistics
        total_checks = len(health_logs)
        online_checks = len([log for log in health_logs if log.status == "online"])
        offline_checks = len([log for log in health_logs if log.status == "offline"])
        error_checks = len([log for log in health_logs if log.status == "error"])
        
        avg_response_time = None
        if health_logs:
            response_times = [log.response_time_ms for log in health_logs if log.response_time_ms is not None]
            if response_times:
                avg_response_time = sum(response_times) / len(response_times)
        
        return {
            "service": {
                "id": service.id,
                "name": service.name,
                "base_url": service.base_url,
                "current_status": service.status
            },
            "statistics": {
                "total_checks": total_checks,
                "online_checks": online_checks,
                "offline_checks": offline_checks,
                "error_checks": error_checks,
                "uptime_percentage": (online_checks / total_checks * 100) if total_checks > 0 else 0,
                "average_response_time_ms": avg_response_time
            },
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "recent_logs": [
                {
                    "status": log.status,
                    "response_time_ms": log.response_time_ms,
                    "error_message": log.error_message,
                    "checked_at": log.checked_at.isoformat()
                }
                for log in health_logs[:10]  # Last 10 checks
            ]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service health history: {e}")
        raise HTTPException(status_code=500, detail="Failed to get service health history")


@router.get("/metrics/response-times")
async def get_response_time_metrics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    db: Session = Depends(get_db)
):
    """
    Get response time metrics across all services.
    
    Args:
        hours: Number of hours to look back
        db: Database session
        
    Returns:
        Response time metrics and statistics
    """
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get all services
        services = db.query(LLMServiceModel).all()
        
        metrics = {}
        for service in services:
            # Get health logs for this service
            health_logs = db.query(ServiceHealthLog).filter(
                ServiceHealthLog.service_id == service.id,
                ServiceHealthLog.checked_at >= start_time,
                ServiceHealthLog.checked_at <= end_time,
                ServiceHealthLog.response_time_ms.isnot(None)
            ).all()
            
            if health_logs:
                response_times = [log.response_time_ms for log in health_logs]
                metrics[service.name] = {
                    "service_id": service.id,
                    "total_requests": len(response_times),
                    "average_response_time_ms": sum(response_times) / len(response_times),
                    "min_response_time_ms": min(response_times),
                    "max_response_time_ms": max(response_times),
                    "p95_response_time_ms": sorted(response_times)[int(len(response_times) * 0.95)] if len(response_times) > 0 else None,
                    "p99_response_time_ms": sorted(response_times)[int(len(response_times) * 0.99)] if len(response_times) > 0 else None
                }
            else:
                metrics[service.name] = {
                    "service_id": service.id,
                    "total_requests": 0,
                    "average_response_time_ms": None,
                    "min_response_time_ms": None,
                    "max_response_time_ms": None,
                    "p95_response_time_ms": None,
                    "p99_response_time_ms": None
                }
        
        return {
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "services": metrics,
            "overall": {
                "total_requests": sum(m["total_requests"] for m in metrics.values()),
                "average_response_time_ms": sum(
                    m["average_response_time_ms"] or 0 for m in metrics.values()
                ) / len([m for m in metrics.values() if m["average_response_time_ms"] is not None]) if any(m["average_response_time_ms"] for m in metrics.values()) else None
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get response time metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get response time metrics")


@router.get("/metrics/uptime")
async def get_uptime_metrics(
    hours: int = Query(24, ge=1, le=168, description="Number of hours to look back"),
    db: Session = Depends(get_db)
):
    """
    Get uptime metrics for all services.
    
    Args:
        hours: Number of hours to look back
        db: Database session
        
    Returns:
        Uptime metrics and statistics
    """
    try:
        # Calculate time range
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours)
        
        # Get all services
        services = db.query(LLMServiceModel).all()
        
        uptime_metrics = {}
        for service in services:
            # Get health logs for this service
            health_logs = db.query(ServiceHealthLog).filter(
                ServiceHealthLog.service_id == service.id,
                ServiceHealthLog.checked_at >= start_time,
                ServiceHealthLog.checked_at <= end_time
            ).all()
            
            if health_logs:
                total_checks = len(health_logs)
                online_checks = len([log for log in health_logs if log.status == "online"])
                offline_checks = len([log for log in health_logs if log.status == "offline"])
                error_checks = len([log for log in health_logs if log.status == "error"])
                
                uptime_metrics[service.name] = {
                    "service_id": service.id,
                    "total_checks": total_checks,
                    "online_checks": online_checks,
                    "offline_checks": offline_checks,
                    "error_checks": error_checks,
                    "uptime_percentage": (online_checks / total_checks * 100) if total_checks > 0 else 0,
                    "downtime_percentage": ((offline_checks + error_checks) / total_checks * 100) if total_checks > 0 else 0,
                    "current_status": service.status
                }
            else:
                uptime_metrics[service.name] = {
                    "service_id": service.id,
                    "total_checks": 0,
                    "online_checks": 0,
                    "offline_checks": 0,
                    "error_checks": 0,
                    "uptime_percentage": 0,
                    "downtime_percentage": 0,
                    "current_status": service.status
                }
        
        # Calculate overall uptime
        total_checks = sum(m["total_checks"] for m in uptime_metrics.values())
        total_online = sum(m["online_checks"] for m in uptime_metrics.values())
        
        return {
            "time_range": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "hours": hours
            },
            "services": uptime_metrics,
            "overall": {
                "total_checks": total_checks,
                "total_online": total_online,
                "overall_uptime_percentage": (total_online / total_checks * 100) if total_checks > 0 else 0
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to get uptime metrics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get uptime metrics")


@router.get("/logs")
async def get_system_logs(
    level: Optional[str] = Query(None, description="Log level filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of log entries"),
    db: Session = Depends(get_db)
):
    """
    Get system logs (placeholder for future log aggregation).
    
    Args:
        level: Optional log level filter
        limit: Maximum number of log entries to return
        db: Database session
        
    Returns:
        System log entries
    """
    try:
        # This is a placeholder - in a real implementation, you would
        # integrate with a proper logging system like ELK stack or similar
        return {
            "message": "Log aggregation not yet implemented",
            "suggestion": "Consider integrating with ELK stack, Fluentd, or similar logging solution",
            "logs": []
        }
        
    except Exception as e:
        logger.error(f"Failed to get system logs: {e}")
        raise HTTPException(status_code=500, detail="Failed to get system logs")
