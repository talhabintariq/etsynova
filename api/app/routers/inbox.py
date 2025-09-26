from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.models.inbox import MockEmailData
from app.services.gmail_client import GmailClient
# from app.agent.graph import EtsyAdviceGraph  # TODO: Import when needed
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/inbox", tags=["inbox"])

# Mock AI draft responses for testing
MOCK_AI_DRAFTS = {
    "mock_gmail_1": {
        "draft_content": "Hi Sarah,\n\nThank you for your order! Your custom necklace is currently in production and should be ready to ship within 2-3 business days. \n\nRegarding the chain length change from 16\" to 18\" - absolutely! I can make that adjustment for you at no additional cost since the piece is still being crafted.\n\nI'll keep you updated on the progress and send you tracking information once it ships.\n\nBest regards,\n[Your Name]",
        "rationale": "Customer has a legitimate question about order status and wants to make a modification. This is a straightforward customer service response that acknowledges their request, provides an update, and confirms the modification can be made.",
        "confidence": 0.92
    },
    "mock_gmail_2": {
        "draft_content": "Hi Mike,\n\nI'm so sorry to hear that your ceramic mug arrived damaged! That's definitely not the quality I strive for.\n\nI'd be happy to send you a replacement mug right away at no charge. Alternatively, I can process a full refund if you prefer.\n\nCould you please let me know which option you'd prefer? If you choose the replacement, I can have it shipped out today with extra protective packaging.\n\nThank you for the photos offer - if you could send them, it would help me improve my packaging process.\n\nSincerely,\n[Your Name]",
        "rationale": "Customer received damaged goods and is requesting a refund. This response shows empathy, takes responsibility, offers solutions (replacement or refund), and asks for feedback to improve. High priority due to product quality issue.",
        "confidence": 0.95
    },
    "mock_gmail_5": {
        "draft_content": "Hi Lisa,\n\nCongratulations on your upcoming wedding! I'd be delighted to help with your wedding favors.\n\nFor an order of 50 lavender soaps, I can offer a 15% bulk discount, bringing the price to $8.50 per soap (normally $10 each). The total would be $425.\n\nI can definitely have them ready by August 15th - that gives us plenty of time to ensure they're perfect for your special day. Each soap will be individually wrapped and can include a small thank-you tag if you'd like.\n\nWould you like me to prepare a formal quote, or do you have any questions about customization options?\n\nBest wishes for your wedding planning!\n\n[Your Name]",
        "rationale": "Potential bulk order with specific deadline and wedding context. Response includes pricing, confirms timeline feasibility, suggests value-adds, and maintains enthusiastic tone appropriate for wedding context. High priority due to large order potential.",
        "confidence": 0.90
    }
}

@router.get("/messages")
async def get_inbox_messages(
    source: Optional[str] = Query(None, description="Filter by source: gmail, etsy, all"),
    filter_type: Optional[str] = Query("all", description="Filter type: all, needs_reply, refunds"),
    limit: int = Query(50, description="Number of messages to return"),
    offset: int = Query(0, description="Pagination offset")
):
    """Get inbox messages with filtering"""

    try:
        # Mock mode always returns mock data
        mock_mode = os.getenv("MOCK_MODE", "false") == "true"

        if mock_mode:
            messages = MockEmailData.get_mock_emails()
        else:
            # TODO: Fetch from database and Gmail API
            messages = MockEmailData.get_mock_emails()

        # Apply filters
        filtered_messages = messages

        if source and source != "all":
            if source == "gmail":
                # In mock mode, all messages are Gmail
                pass
            elif source == "etsy":
                # Filter for Etsy conversations (not implemented in mock)
                filtered_messages = []

        if filter_type != "all":
            if filter_type == "needs_reply":
                filtered_messages = [m for m in filtered_messages if m.get("needs_reply", False)]
            elif filter_type == "refunds":
                filtered_messages = [m for m in filtered_messages if m.get("is_refund_related", False)]

        # Pagination
        total_count = len(filtered_messages)
        paginated_messages = filtered_messages[offset:offset + limit]

        return {
            "messages": paginated_messages,
            "total": total_count,
            "limit": limit,
            "offset": offset,
            "filters_applied": {
                "source": source or "all",
                "filter_type": filter_type
            }
        }

    except Exception as e:
        logger.error(f"Failed to get inbox messages: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/messages/{message_id}")
async def get_message_details(message_id: str):
    """Get detailed view of a specific message"""

    try:
        mock_mode = os.getenv("MOCK_MODE", "false") == "true"

        if mock_mode:
            mock_emails = MockEmailData.get_mock_emails()
            for email in mock_emails:
                if email["id"] == message_id:
                    return {
                        "message": email,
                        "thread_messages": [email],  # Simplified - in reality would fetch full thread
                        "linked_orders": [email["etsy_receipt_id"]] if email.get("etsy_receipt_id") else [],
                        "previous_drafts": []  # TODO: Fetch from message_audit
                    }

            raise HTTPException(status_code=404, detail="Message not found")

        # TODO: Implement real Gmail API fetching
        raise HTTPException(status_code=501, detail="Real Gmail fetching not implemented yet")

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get message details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/{message_id}/draft")
async def generate_draft_reply(message_id: str):
    """Generate AI draft reply for a message"""

    try:
        mock_mode = os.getenv("MOCK_MODE", "false") == "true"

        if mock_mode:
            # Return mock draft if available
            if message_id in MOCK_AI_DRAFTS:
                draft_data = MOCK_AI_DRAFTS[message_id]

                # Simulate AI generation latency
                import asyncio
                await asyncio.sleep(1.5)  # Simulate processing time

                # TODO: Store in message_audit table
                audit_record = {
                    "source_message_id": message_id,
                    "source_type": "gmail",
                    "action_type": "draft_generated",
                    "draft_content": draft_data["draft_content"],
                    "ai_rationale": draft_data["rationale"],
                    "ai_model": "mock-gpt-4",
                    "generation_latency_ms": 1500,
                    "created_at": datetime.utcnow().isoformat()
                }

                return {
                    "draft_id": f"draft_{message_id}_{int(datetime.utcnow().timestamp())}",
                    "message_id": message_id,
                    "draft_content": draft_data["draft_content"],
                    "rationale": draft_data["rationale"],
                    "confidence_score": draft_data.get("confidence", 0.8),
                    "generation_time_ms": 1500,
                    "model_used": "mock-gpt-4",
                    "audit_id": audit_record,
                    "actions_available": ["approve", "edit", "reject", "copy"]
                }
            else:
                # Generic draft for unknown messages
                return {
                    "draft_id": f"draft_{message_id}_generic",
                    "message_id": message_id,
                    "draft_content": "Thank you for your message. I'll get back to you soon with more details.",
                    "rationale": "Generic response for messages without specific context",
                    "confidence_score": 0.6,
                    "generation_time_ms": 800,
                    "model_used": "mock-gpt-4"
                }

        # TODO: Implement real AI draft generation
        mock_emails = MockEmailData.get_mock_emails()
        message = next((m for m in mock_emails if m["id"] == message_id), None)
        if not message:
            raise HTTPException(status_code=404, detail="Message not found")

        # Initialize AI agent
        llm_provider = os.getenv("LLM_PROVIDER", "none")
        if llm_provider == "none":
            raise HTTPException(status_code=501, detail="AI drafts require LLM_PROVIDER to be configured")

        # TODO: Use EtsyAdviceGraph to generate contextual response
        # For now, return a generic response
        return {
            "draft_id": f"draft_{message_id}_ai",
            "message_id": message_id,
            "draft_content": "Thank you for reaching out. I'll review your message and get back to you soon.",
            "rationale": "Generic AI response - full context analysis not yet implemented",
            "confidence_score": 0.5,
            "generation_time_ms": 2000,
            "model_used": llm_provider
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate draft: {e}")
        raise HTTPException(status_code=500, detail=f"Draft generation failed: {str(e)}")

@router.post("/messages/{message_id}/draft/{draft_id}/approve")
async def approve_draft(message_id: str, draft_id: str, action: str = "copy"):
    """Approve an AI-generated draft"""

    try:
        # TODO: Store approval in message_audit
        audit_record = {
            "source_message_id": message_id,
            "source_type": "gmail",
            "action_type": "draft_approved",
            "approved_by": "user",  # TODO: Get from session
            "approval_action": action,
            "created_at": datetime.utcnow().isoformat()
        }

        if action == "copy":
            return {
                "draft_id": draft_id,
                "message_id": message_id,
                "action": "copied",
                "message": "Draft copied to clipboard. You can now paste it into your email client.",
                "audit_id": audit_record
            }
        elif action == "send":
            # TODO: Implement actual sending for Etsy messages
            return {
                "draft_id": draft_id,
                "message_id": message_id,
                "action": "sent",
                "message": "Message sent successfully (mock mode)",
                "audit_id": audit_record
            }
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Use 'copy' or 'send'")

    except Exception as e:
        logger.error(f"Failed to approve draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/messages/{message_id}/draft/{draft_id}/reject")
async def reject_draft(message_id: str, draft_id: str, feedback: Optional[str] = None):
    """Reject an AI-generated draft"""

    try:
        # TODO: Store rejection in message_audit
        audit_record = {
            "source_message_id": message_id,
            "source_type": "gmail",
            "action_type": "draft_rejected",
            "approved_by": "user",  # TODO: Get from session
            "approval_action": "rejected",
            "human_edits": feedback,
            "created_at": datetime.utcnow().isoformat()
        }

        return {
            "draft_id": draft_id,
            "message_id": message_id,
            "action": "rejected",
            "message": "Draft rejected. Feedback recorded for model improvement.",
            "audit_id": audit_record
        }

    except Exception as e:
        logger.error(f"Failed to reject draft: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/gmail/sync")
async def sync_gmail_messages():
    """Manually trigger Gmail sync"""

    try:
        mock_mode = os.getenv("MOCK_MODE", "false") == "true"

        if mock_mode:
            import asyncio
            await asyncio.sleep(2)  # Simulate sync time

            return {
                "synced": True,
                "messages_fetched": 5,
                "new_messages": 2,
                "last_sync": datetime.utcnow().isoformat(),
                "mode": "mock"
            }

        # TODO: Implement real Gmail sync using GmailClient
        gmail_client = GmailClient()
        result = await gmail_client.sync_messages(max_results=50)

        return {
            "synced": True,
            "messages_fetched": result["total"],
            "new_messages": result["synced"],
            "last_sync": result["last_sync"],
            "mode": "live"
        }

    except Exception as e:
        logger.error(f"Gmail sync failed: {e}")
        raise HTTPException(status_code=500, detail=f"Sync failed: {str(e)}")

@router.get("/stats")
async def get_inbox_stats():
    """Get inbox statistics"""

    try:
        mock_mode = os.getenv("MOCK_MODE", "false") == "true"

        if mock_mode:
            mock_emails = MockEmailData.get_mock_emails()

            return {
                "total_messages": len(mock_emails),
                "unread_count": sum(1 for m in mock_emails if m.get("is_unread", False)),
                "needs_reply_count": sum(1 for m in mock_emails if m.get("needs_reply", False)),
                "refund_requests": sum(1 for m in mock_emails if m.get("is_refund_related", False)),
                "linked_to_orders": sum(1 for m in mock_emails if m.get("etsy_receipt_id")),
                "sources": {
                    "gmail": len(mock_emails),
                    "etsy": 0  # Not implemented in mock
                },
                "avg_response_time_hours": 4.2,
                "last_sync": datetime.utcnow().isoformat()
            }

        # TODO: Calculate real stats from database
        return {
            "total_messages": 0,
            "unread_count": 0,
            "needs_reply_count": 0,
            "refund_requests": 0,
            "linked_to_orders": 0,
            "sources": {"gmail": 0, "etsy": 0},
            "last_sync": None
        }

    except Exception as e:
        logger.error(f"Failed to get inbox stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))