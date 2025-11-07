"""
Article Request API Endpoints
Handles user-driven article generation requests and thinking contributions
"""

from fastapi import APIRouter, HTTPException, Depends, Query, Header
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/article-requests", tags=["article-requests"])


# Pydantic models for request/response
class ArticleRequestCreate(BaseModel):
    title: str
    topic: str
    article_type: str = "analysis"
    desired_angle: Optional[str] = None
    key_points: Optional[List[str]] = None
    required_sources: Optional[List[str]] = None
    exclude_sources: Optional[List[str]] = None
    background_context: Optional[str] = None
    estimated_length: str = "medium"
    target_audience: str = "general_public"
    priority: int = 1


class UserThinkingCreate(BaseModel):
    thinking_content: str
    stage: str  # pre_generation, draft_review, refinement, final
    thinking_type: str  # suggestion, perspective, fact_check, improvement, analysis
    adoption_priority: int = 5


class ArticleRequestResponse(BaseModel):
    id: str
    title: str
    topic: str
    status: str
    priority: int
    created_date: str
    
    class Config:
        from_attributes = True


def get_current_user_id(x_user_id: str = Header(None)) -> str:
    """Extract user ID from header. In production, this would validate JWT"""
    if not x_user_id:
        raise HTTPException(status_code=401, detail="User ID required in X-User-ID header")
    return x_user_id


@router.post("/request", response_model=dict)
async def create_article_request(
    request_data: ArticleRequestCreate,
    user_id: str = Depends(get_current_user_id),
    db = Depends(None)  # Would inject real DB
):
    """
    Create a new article request
    
    **User must be registered and provide X-User-ID header**
    
    Example request:
    ```json
    {
        "title": "Zimbabwe's Economic Recovery Strategy",
        "topic": "Zimbabwe economy",
        "article_type": "analysis",
        "desired_angle": "Focus on fiscal policy measures",
        "key_points": ["Currency stability", "Inflation control", "GDP growth"],
        "background_context": "Needed for investor briefing",
        "priority": 3,
        "deadline": "2024-02-15T10:00:00"
    }
    ```
    """
    try:
        from src.services.article_request_service import ArticleRequestManager
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        manager = ArticleRequestManager(db)
        
        result = manager.create_request(
            user_id=user_id,
            title=request_data.title,
            topic=request_data.topic,
            article_type=request_data.article_type,
            desired_angle=request_data.desired_angle,
            key_points=request_data.key_points,
            required_sources=request_data.required_sources,
            exclude_sources=request_data.exclude_sources,
            background_context=request_data.background_context,
            estimated_length=request_data.estimated_length,
            target_audience=request_data.target_audience,
            priority=request_data.priority
        )
        
        db.close()
        
        if result.get("status") == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message"))
    
    except Exception as e:
        logger.error(f"Error creating article request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/request/{request_id}", response_model=dict)
async def get_article_request(
    request_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get details of a specific article request"""
    try:
        from src.services.article_request_service import ArticleRequestManager
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        manager = ArticleRequestManager(db)
        
        request_dict = manager.get_request(request_id)
        db.close()
        
        if not request_dict:
            raise HTTPException(status_code=404, detail="Article request not found")
        
        return {
            "status": "success",
            "data": request_dict
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching article request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/my-requests", response_model=dict)
async def get_my_requests(
    status: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """
    Get all article requests for the current user
    
    Optional query parameters:
    - status: Filter by status (pending, assigned, in_progress, completed, rejected)
    """
    try:
        from src.services.article_request_service import ArticleRequestManager
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        manager = ArticleRequestManager(db)
        
        requests = manager.get_user_requests(user_id, status=status)
        db.close()
        
        return {
            "status": "success",
            "count": len(requests),
            "data": requests
        }
    
    except Exception as e:
        logger.error(f"Error fetching user requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pending", response_model=dict)
async def get_pending_requests(
    user_id: str = Depends(get_current_user_id)
):
    """Get all pending article requests (admin/reviewer only)"""
    try:
        from src.services.article_request_service import ArticleRequestManager
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        manager = ArticleRequestManager(db)
        
        requests = manager.get_pending_requests()
        db.close()
        
        return {
            "status": "success",
            "count": len(requests),
            "data": requests
        }
    
    except Exception as e:
        logger.error(f"Error fetching pending requests: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/thinking", response_model=dict)
async def add_user_thinking(
    request_id: str,
    thinking_data: UserThinkingCreate,
    user_id: str = Depends(get_current_user_id)
):
    """
    Add user thinking/contribution to an article request
    
    **At multiple stages:**
    - `pre_generation`: Initial ideas before article is written
    - `draft_review`: Feedback on draft article
    - `refinement`: Suggestions for improvement
    - `final`: Final recommendations
    
    Example request:
    ```json
    {
        "thinking_content": "Consider including recent IMF statements on Zimbabwe's monetary policy",
        "stage": "pre_generation",
        "thinking_type": "suggestion",
        "adoption_priority": 8
    }
    ```
    """
    try:
        from src.services.article_request_service import UserThinkingManager
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        manager = UserThinkingManager(db)
        
        result = manager.add_thinking(
            user_id=user_id,
            thinking_content=thinking_data.thinking_content,
            stage=thinking_data.stage,
            thinking_type=thinking_data.thinking_type,
            article_request_id=request_id,
            adoption_priority=thinking_data.adoption_priority
        )
        
        db.close()
        
        if result.get("status") == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding user thinking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{request_id}/thinking", response_model=dict)
async def get_request_thinking(
    request_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """Get all thinking contributions for an article request"""
    try:
        from src.services.article_request_service import UserThinkingManager
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        manager = UserThinkingManager(db)
        
        thinking_list = manager.get_thinking_for_request(request_id)
        db.close()
        
        return {
            "status": "success",
            "count": len(thinking_list),
            "data": thinking_list
        }
    
    except Exception as e:
        logger.error(f"Error fetching request thinking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{request_id}/orchestration", response_model=dict)
async def get_orchestration_summary(
    request_id: str,
    user_id: str = Depends(get_current_user_id)
):
    """
    Get comprehensive summary of a request with all its user thinking
    
    Returns the full orchestration view including:
    - Request details
    - All user thinking contributions
    - Thinking organized by stage and type
    - Average priority score
    """
    try:
        from src.services.article_request_service import ArticleGenerationOrchestrator
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        orchestrator = ArticleGenerationOrchestrator(db)
        
        summary = orchestrator.get_orchestration_summary(request_id)
        db.close()
        
        if summary.get("status") == "success":
            return summary
        else:
            raise HTTPException(status_code=404, detail=summary.get("message"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting orchestration summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/generate", response_model=dict)
async def generate_article_from_request(
    request_id: str,
    include_user_thinking: bool = Query(True),
    user_id: str = Depends(get_current_user_id)
):
    """
    Trigger article generation from a user request
    
    This endpoint:
    1. Takes the user request and all contributed thinking
    2. Generates an article incorporating user input
    3. Marks thinking contributions as used
    4. Updates request status to 'completed'
    
    Query parameters:
    - include_user_thinking: Whether to incorporate user thinking (default: true)
    """
    try:
        from src.services.article_request_service import ArticleGenerationOrchestrator
        from src.services.unified_analyzer import UnifiedContentAnalyzer
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        orchestrator = ArticleGenerationOrchestrator(db)
        
        # Create a generation service instance
        analyzer = UnifiedContentAnalyzer(db)
        
        result = orchestrator.generate_from_request(
            request_id=request_id,
            generation_service=analyzer,
            include_user_thinking=include_user_thinking
        )
        
        db.close()
        
        if result.get("status") == "success":
            return result
        else:
            raise HTTPException(status_code=400, detail=result.get("message"))
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating article from request: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/user/{user_id}/thinking", response_model=dict)
async def get_user_thinking(
    user_id: str,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Get all thinking contributions from a specific user
    
    Only the user themselves or admins can view this
    """
    try:
        # Check authorization
        if user_id != current_user_id:
            # In production, check if current_user_id is admin
            pass
        
        from src.services.article_request_service import UserThinkingManager
        from src.db.session import SessionLocal
        
        db = SessionLocal()
        manager = UserThinkingManager(db)
        
        thinking_list = manager.get_user_thinking(user_id)
        db.close()
        
        return {
            "status": "success",
            "count": len(thinking_list),
            "data": thinking_list
        }
    
    except Exception as e:
        logger.error(f"Error fetching user thinking: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{request_id}/status/{new_status}", response_model=dict)
async def update_request_status(
    request_id: str,
    new_status: str,
    rejection_reason: Optional[str] = Query(None),
    user_id: str = Depends(get_current_user_id)
):
    """
    Update the status of an article request (admin/reviewer only)
    
    Valid statuses: pending, assigned, in_progress, completed, rejected
    """
    try:
        from src.services.article_request_service import ArticleRequestManager
        from src.db.session import SessionLocal
        
        valid_statuses = ["pending", "assigned", "in_progress", "completed", "rejected"]
        if new_status not in valid_statuses:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Must be one of: {valid_statuses}"
            )
        
        db = SessionLocal()
        manager = ArticleRequestManager(db)
        
        success = manager.update_request_status(
            request_id,
            new_status,
            rejection_reason=rejection_reason
        )
        
        db.close()
        
        if success:
            return {
                "status": "success",
                "message": f"Request status updated to {new_status}"
            }
        else:
            raise HTTPException(status_code=404, detail="Article request not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating request status: {e}")
        raise HTTPException(status_code=500, detail=str(e))