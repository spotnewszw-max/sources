"""
Article Request Service - Handles user-driven article generation
Manages user article requests, thinking contributions, and orchestrates article generation
"""

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)


class ArticleRequestManager:
    """Manages article requests from users"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def create_request(
        self,
        user_id: str,
        title: str,
        topic: str,
        article_type: str = "analysis",
        desired_angle: Optional[str] = None,
        key_points: Optional[List[str]] = None,
        required_sources: Optional[List[str]] = None,
        exclude_sources: Optional[List[str]] = None,
        background_context: Optional[str] = None,
        deadline: Optional[datetime] = None,
        estimated_length: str = "medium",
        target_audience: str = "general_public",
        priority: int = 1
    ) -> Dict[str, Any]:
        """
        Create a new article request from a user
        
        Args:
            user_id: ID of the requesting user
            title: Requested article title
            topic: Main topic
            article_type: Type of article (historical, present, future, analysis)
            desired_angle: Specific perspective to take
            key_points: Points that must be included
            required_sources: Sources that must be used
            exclude_sources: Sources to avoid
            background_context: Why this article is needed
            deadline: When the article is needed
            estimated_length: Desired length (short, medium, long)
            target_audience: Who is this for
            priority: Urgency level (1-5)
        
        Returns:
            Dict with request details and status
        """
        try:
            from src.db.models import ArticleRequest
            
            request = ArticleRequest(
                title=title,
                topic=topic,
                article_type=article_type,
                desired_angle=desired_angle,
                key_points=key_points or [],
                required_sources=required_sources or [],
                exclude_sources=exclude_sources or [],
                background_context=background_context,
                deadline=deadline,
                estimated_length=estimated_length,
                target_audience=target_audience,
                priority=priority,
                requested_by_id=user_id,
                status="pending"
            )
            
            self.db.add(request)
            self.db.commit()
            self.db.refresh(request)
            
            logger.info(f"Article request created: {request.id} for user {user_id}")
            
            return {
                "id": request.id,
                "status": "success",
                "message": f"Article request '{title}' created successfully",
                "request_id": request.id,
                "topic": topic,
                "priority": priority,
                "deadline": deadline.isoformat() if deadline else None
            }
        
        except Exception as e:
            logger.error(f"Error creating article request: {e}")
            self.db.rollback()
            return {
                "status": "error",
                "message": f"Failed to create article request: {str(e)}"
            }
    
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific article request"""
        try:
            from src.db.models import ArticleRequest
            
            request = self.db.query(ArticleRequest).filter(
                ArticleRequest.id == request_id
            ).first()
            
            if not request:
                return None
            
            return self._request_to_dict(request)
        
        except Exception as e:
            logger.error(f"Error fetching article request: {e}")
            return None
    
    def get_user_requests(
        self,
        user_id: str,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get all article requests for a user"""
        try:
            from src.db.models import ArticleRequest
            
            query = self.db.query(ArticleRequest).filter(
                ArticleRequest.requested_by_id == user_id
            )
            
            if status:
                query = query.filter(ArticleRequest.status == status)
            
            requests = query.order_by(
                ArticleRequest.priority.desc(),
                ArticleRequest.created_date.desc()
            ).limit(limit).all()
            
            return [self._request_to_dict(r) for r in requests]
        
        except Exception as e:
            logger.error(f"Error fetching user requests: {e}")
            return []
    
    def get_pending_requests(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all pending article requests"""
        try:
            from src.db.models import ArticleRequest
            
            requests = self.db.query(ArticleRequest).filter(
                ArticleRequest.status.in_(["pending", "assigned"])
            ).order_by(
                ArticleRequest.priority.desc(),
                ArticleRequest.created_date.asc()
            ).limit(limit).all()
            
            return [self._request_to_dict(r) for r in requests]
        
        except Exception as e:
            logger.error(f"Error fetching pending requests: {e}")
            return []
    
    def update_request_status(
        self,
        request_id: str,
        status: str,
        rejection_reason: Optional[str] = None,
        generated_article_id: Optional[str] = None
    ) -> bool:
        """Update the status of an article request"""
        try:
            from src.db.models import ArticleRequest
            
            request = self.db.query(ArticleRequest).filter(
                ArticleRequest.id == request_id
            ).first()
            
            if not request:
                return False
            
            request.status = status
            
            if status == "assigned":
                request.assigned_date = datetime.utcnow()
            elif status == "completed":
                request.completed_date = datetime.utcnow()
                if generated_article_id:
                    request.generated_article_id = generated_article_id
            elif status == "rejected":
                request.rejection_reason = rejection_reason
            
            self.db.commit()
            logger.info(f"Article request {request_id} status updated to {status}")
            return True
        
        except Exception as e:
            logger.error(f"Error updating request status: {e}")
            self.db.rollback()
            return False
    
    def _request_to_dict(self, request) -> Dict[str, Any]:
        """Convert ArticleRequest object to dictionary"""
        return {
            "id": request.id,
            "title": request.title,
            "topic": request.topic,
            "article_type": request.article_type,
            "desired_angle": request.desired_angle,
            "key_points": request.key_points,
            "required_sources": request.required_sources,
            "exclude_sources": request.exclude_sources,
            "background_context": request.background_context,
            "deadline": request.deadline.isoformat() if request.deadline else None,
            "estimated_length": request.estimated_length,
            "target_audience": request.target_audience,
            "status": request.status,
            "priority": request.priority,
            "requested_by_id": request.requested_by_id,
            "generated_article_id": request.generated_article_id,
            "created_date": request.created_date.isoformat(),
            "assigned_date": request.assigned_date.isoformat() if request.assigned_date else None,
            "completed_date": request.completed_date.isoformat() if request.completed_date else None,
            "rejection_reason": request.rejection_reason
        }


class UserThinkingManager:
    """Manages user thinking contributions during article construction"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
    
    def add_thinking(
        self,
        user_id: str,
        thinking_content: str,
        stage: str = "draft_review",
        thinking_type: str = "suggestion",
        article_request_id: Optional[str] = None,
        generated_article_id: Optional[str] = None,
        adoption_priority: int = 5
    ) -> Dict[str, Any]:
        """
        Add user thinking during article construction
        
        Args:
            user_id: ID of contributing user
            thinking_content: The actual thinking/suggestion
            stage: Stage in article construction (pre_generation, draft_review, refinement, final)
            thinking_type: Type (suggestion, perspective, fact_check, improvement, analysis)
            article_request_id: Associated article request (optional)
            generated_article_id: Associated generated article (optional)
            adoption_priority: Priority for incorporation (0-10)
        
        Returns:
            Dict with thinking details and status
        """
        try:
            from src.db.models import UserThinking, User
            
            # Verify user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                return {
                    "status": "error",
                    "message": "User not found"
                }
            
            thinking = UserThinking(
                contributed_by_id=user_id,
                thinking_content=thinking_content,
                stage=stage,
                thinking_type=thinking_type,
                article_request_id=article_request_id,
                generated_article_id=generated_article_id,
                adoption_priority=adoption_priority,
                is_visible_to_team=True
            )
            
            self.db.add(thinking)
            
            # Update user stats
            user.thinking_contributions += 1
            
            self.db.commit()
            self.db.refresh(thinking)
            
            logger.info(f"User thinking added: {thinking.id} by user {user_id} at stage {stage}")
            
            return {
                "status": "success",
                "message": "Your thinking has been recorded",
                "thinking_id": thinking.id,
                "stage": stage,
                "thinking_type": thinking_type
            }
        
        except Exception as e:
            logger.error(f"Error adding user thinking: {e}")
            self.db.rollback()
            return {
                "status": "error",
                "message": f"Failed to add thinking: {str(e)}"
            }
    
    def get_thinking_for_request(self, request_id: str) -> List[Dict[str, Any]]:
        """Get all thinking contributions for an article request"""
        try:
            from src.db.models import UserThinking
            
            thinking_list = self.db.query(UserThinking).filter(
                UserThinking.article_request_id == request_id
            ).order_by(
                UserThinking.adoption_priority.desc(),
                UserThinking.created_date.asc()
            ).all()
            
            return [self._thinking_to_dict(t) for t in thinking_list]
        
        except Exception as e:
            logger.error(f"Error fetching thinking for request: {e}")
            return []
    
    def get_thinking_for_article(self, article_id: str) -> List[Dict[str, Any]]:
        """Get all thinking contributions for a generated article"""
        try:
            from src.db.models import UserThinking
            
            thinking_list = self.db.query(UserThinking).filter(
                UserThinking.generated_article_id == article_id
            ).order_by(
                UserThinking.adoption_priority.desc(),
                UserThinking.created_date.asc()
            ).all()
            
            return [self._thinking_to_dict(t) for t in thinking_list]
        
        except Exception as e:
            logger.error(f"Error fetching thinking for article: {e}")
            return []
    
    def get_user_thinking(self, user_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get all thinking contributions from a specific user"""
        try:
            from src.db.models import UserThinking
            
            thinking_list = self.db.query(UserThinking).filter(
                UserThinking.contributed_by_id == user_id
            ).order_by(
                UserThinking.created_date.desc()
            ).limit(limit).all()
            
            return [self._thinking_to_dict(t) for t in thinking_list]
        
        except Exception as e:
            logger.error(f"Error fetching user thinking: {e}")
            return []
    
    def mark_thinking_used(
        self,
        thinking_id: str,
        impact_notes: Optional[str] = None,
        helpfulness_score: Optional[float] = None
    ) -> bool:
        """Mark a thinking contribution as used"""
        try:
            from src.db.models import UserThinking
            
            thinking = self.db.query(UserThinking).filter(
                UserThinking.id == thinking_id
            ).first()
            
            if not thinking:
                return False
            
            thinking.was_used = True
            if impact_notes:
                thinking.impact_notes = impact_notes
            if helpfulness_score is not None:
                thinking.helpfulness_score = helpfulness_score
            
            self.db.commit()
            logger.info(f"Thinking {thinking_id} marked as used")
            return True
        
        except Exception as e:
            logger.error(f"Error marking thinking as used: {e}")
            self.db.rollback()
            return False
    
    def get_thinking_by_stage(
        self,
        stage: str,
        article_request_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get thinking contributions at a specific stage"""
        try:
            from src.db.models import UserThinking
            
            query = self.db.query(UserThinking).filter(
                UserThinking.stage == stage
            )
            
            if article_request_id:
                query = query.filter(
                    UserThinking.article_request_id == article_request_id
                )
            
            thinking_list = query.order_by(
                UserThinking.adoption_priority.desc(),
                UserThinking.created_date.asc()
            ).all()
            
            return [self._thinking_to_dict(t) for t in thinking_list]
        
        except Exception as e:
            logger.error(f"Error fetching thinking by stage: {e}")
            return []
    
    def _thinking_to_dict(self, thinking) -> Dict[str, Any]:
        """Convert UserThinking object to dictionary"""
        return {
            "id": thinking.id,
            "article_request_id": thinking.article_request_id,
            "generated_article_id": thinking.generated_article_id,
            "contributed_by_id": thinking.contributed_by_id,
            "stage": thinking.stage,
            "thinking_content": thinking.thinking_content,
            "thinking_type": thinking.thinking_type,
            "was_used": thinking.was_used,
            "impact_notes": thinking.impact_notes,
            "helpfulness_score": thinking.helpfulness_score,
            "adoption_priority": thinking.adoption_priority,
            "created_date": thinking.created_date.isoformat(),
            "updated_date": thinking.updated_date.isoformat()
        }


class ArticleGenerationOrchestrator:
    """Orchestrates article generation with user thinking incorporated"""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.request_manager = ArticleRequestManager(db_session)
        self.thinking_manager = UserThinkingManager(db_session)
    
    def generate_from_request(
        self,
        request_id: str,
        generation_service,
        include_user_thinking: bool = True
    ) -> Dict[str, Any]:
        """
        Generate an article from a user request, incorporating user thinking
        
        Args:
            request_id: ID of the article request
            generation_service: The article generation service to use
            include_user_thinking: Whether to incorporate user thinking
        
        Returns:
            Dict with generation status and article details
        """
        try:
            # Get the request
            request_dict = self.request_manager.get_request(request_id)
            if not request_dict:
                return {
                    "status": "error",
                    "message": "Article request not found"
                }
            
            # Mark as assigned
            self.request_manager.update_request_status(request_id, "assigned")
            
            # Get user thinking if requested
            user_thinking_list = []
            if include_user_thinking:
                user_thinking_list = self.thinking_manager.get_thinking_for_request(request_id)
            
            # Compile user context
            user_context = self._compile_user_context(request_dict, user_thinking_list)
            
            # Call generation service with context
            generation_result = generation_service.generate_article(
                topic=request_dict["topic"],
                article_type=request_dict["article_type"],
                user_context=user_context,
                key_points=request_dict.get("key_points", []),
                required_sources=request_dict.get("required_sources", []),
                exclude_sources=request_dict.get("exclude_sources", [])
            )
            
            if generation_result.get("status") == "success":
                article_id = generation_result.get("article_id")
                
                # Update request with generated article
                self.request_manager.update_request_status(
                    request_id,
                    "completed",
                    generated_article_id=article_id
                )
                
                # Mark thinking as used
                for thinking in user_thinking_list:
                    if thinking.get("thinking_type") in ["suggestion", "improvement", "perspective"]:
                        self.thinking_manager.mark_thinking_used(
                            thinking["id"],
                            impact_notes="Incorporated into article generation",
                            helpfulness_score=0.8
                        )
                
                logger.info(f"Article generated from request {request_id}: {article_id}")
                
                return {
                    "status": "success",
                    "message": f"Article generated successfully",
                    "article_id": article_id,
                    "request_id": request_id,
                    "user_thinking_incorporated": len(user_thinking_list)
                }
            else:
                # Mark as failed
                self.request_manager.update_request_status(
                    request_id,
                    "rejected",
                    rejection_reason="Generation failed: " + generation_result.get("message", "Unknown error")
                )
                
                return {
                    "status": "error",
                    "message": f"Failed to generate article: {generation_result.get('message')}"
                }
        
        except Exception as e:
            logger.error(f"Error in article generation orchestrator: {e}")
            self.request_manager.update_request_status(
                request_id,
                "rejected",
                rejection_reason=f"System error: {str(e)}"
            )
            return {
                "status": "error",
                "message": f"System error during generation: {str(e)}"
            }
    
    def _compile_user_context(
        self,
        request_dict: Dict[str, Any],
        thinking_list: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compile all user input into context for article generation"""
        
        context = {
            "user_request": {
                "title": request_dict.get("title"),
                "desired_angle": request_dict.get("desired_angle"),
                "background_context": request_dict.get("background_context"),
                "target_audience": request_dict.get("target_audience"),
                "estimated_length": request_dict.get("estimated_length")
            },
            "user_thinking_by_stage": {},
            "all_thinking": thinking_list
        }
        
        # Organize thinking by stage
        for thinking in thinking_list:
            stage = thinking.get("stage")
            if stage not in context["user_thinking_by_stage"]:
                context["user_thinking_by_stage"][stage] = []
            context["user_thinking_by_stage"][stage].append(thinking)
        
        return context
    
    def get_orchestration_summary(self, request_id: str) -> Dict[str, Any]:
        """Get comprehensive summary of request and its thinking"""
        try:
            request_dict = self.request_manager.get_request(request_id)
            if not request_dict:
                return {"status": "error", "message": "Request not found"}
            
            thinking_list = self.thinking_manager.get_thinking_for_request(request_id)
            
            return {
                "status": "success",
                "request": request_dict,
                "thinking_contributions": thinking_list,
                "thinking_count": len(thinking_list),
                "thinking_by_type": self._count_by_type(thinking_list),
                "thinking_by_stage": self._count_by_stage(thinking_list),
                "avg_priority": sum(t.get("adoption_priority", 5) for t in thinking_list) / len(thinking_list) if thinking_list else 0
            }
        
        except Exception as e:
            logger.error(f"Error getting orchestration summary: {e}")
            return {
                "status": "error",
                "message": f"Error: {str(e)}"
            }
    
    def _count_by_type(self, thinking_list: List[Dict]) -> Dict[str, int]:
        """Count thinking contributions by type"""
        counts = {}
        for thinking in thinking_list:
            thinking_type = thinking.get("thinking_type", "unknown")
            counts[thinking_type] = counts.get(thinking_type, 0) + 1
        return counts
    
    def _count_by_stage(self, thinking_list: List[Dict]) -> Dict[str, int]:
        """Count thinking contributions by stage"""
        counts = {}
        for thinking in thinking_list:
            stage = thinking.get("stage", "unknown")
            counts[stage] = counts.get(stage, 0) + 1
        return counts