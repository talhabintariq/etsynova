from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from cryptography.fernet import Fernet
import os

Base = declarative_base()

# Encryption key for sensitive data
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', Fernet.generate_key())
cipher_suite = Fernet(ENCRYPTION_KEY)

class OAuthAccount(Base):
    """OAuth accounts for third-party integrations (Google, etc.)"""
    __tablename__ = "oauth_accounts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)  # Maps to shop_id or user identifier
    provider = Column(String, nullable=False)  # 'google', 'etsy', etc.
    provider_user_id = Column(String, nullable=False)  # User ID from the provider
    email = Column(String, nullable=True)  # Associated email address
    access_token = Column(Text, nullable=True)  # Encrypted at rest
    refresh_token = Column(Text, nullable=True)  # Encrypted at rest
    token_expires_at = Column(DateTime, nullable=True)
    scope = Column(String, nullable=True)  # OAuth scopes granted
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    emails = relationship("Email", back_populates="oauth_account")

    def set_encrypted_refresh_token(self, token: str):
        """Encrypt and store refresh token"""
        if token:
            self.refresh_token = cipher_suite.encrypt(token.encode()).decode()

    def get_decrypted_refresh_token(self) -> str:
        """Decrypt and return refresh token"""
        if self.refresh_token:
            return cipher_suite.decrypt(self.refresh_token.encode()).decode()
        return None

    def set_encrypted_access_token(self, token: str):
        """Encrypt and store access token"""
        if token:
            self.access_token = cipher_suite.encrypt(token.encode()).decode()

    def get_decrypted_access_token(self) -> str:
        """Decrypt and return access token"""
        if self.access_token:
            return cipher_suite.decrypt(self.access_token.encode()).decode()
        return None

class Email(Base):
    """Gmail and other email threads"""
    __tablename__ = "emails"

    id = Column(Integer, primary_key=True, index=True)
    oauth_account_id = Column(Integer, ForeignKey("oauth_accounts.id"), nullable=False)

    # Gmail API fields
    message_id = Column(String, unique=True, index=True, nullable=False)  # Gmail message ID
    thread_id = Column(String, index=True, nullable=False)  # Gmail thread ID

    # Message metadata
    from_email = Column(String, nullable=False)
    from_name = Column(String, nullable=True)
    to_emails = Column(JSON, nullable=True)  # Array of recipient emails
    subject = Column(String, nullable=False)
    snippet = Column(Text, nullable=True)  # Gmail snippet/preview
    body_text = Column(Text, nullable=True)
    body_html = Column(Text, nullable=True)

    # Gmail labels and metadata
    labels = Column(JSON, nullable=True)  # Gmail labels array
    is_unread = Column(Boolean, default=True)
    is_important = Column(Boolean, default=False)
    internal_date = Column(DateTime, nullable=False)  # When email was received

    # Etsy linking
    etsy_receipt_id = Column(String, nullable=True, index=True)  # Linked order number
    etsy_listing_id = Column(String, nullable=True, index=True)  # Linked listing
    has_etsy_links = Column(Boolean, default=False, index=True)  # Quick filter

    # AI and response tracking
    needs_reply = Column(Boolean, default=False, index=True)
    reply_priority = Column(String, default='normal')  # 'urgent', 'high', 'normal', 'low'
    is_refund_related = Column(Boolean, default=False, index=True)

    # Retention and compliance
    retention_until = Column(DateTime, nullable=True)  # Auto-delete after this date
    is_linked_to_order = Column(Boolean, default=False)  # Affects retention policy

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    oauth_account = relationship("OAuthAccount", back_populates="emails")
    drafts = relationship("MessageAudit", back_populates="email")

class MessageAudit(Base):
    """Audit log for AI drafts, approvals, and actions"""
    __tablename__ = "message_audit"

    id = Column(Integer, primary_key=True, index=True)
    email_id = Column(Integer, ForeignKey("emails.id"), nullable=True)  # Null for Etsy messages

    # Source and context
    source_type = Column(String, nullable=False)  # 'gmail', 'etsy'
    source_message_id = Column(String, nullable=False)  # Original message ID
    action_type = Column(String, nullable=False)  # 'draft_generated', 'draft_approved', 'message_sent', 'draft_rejected'

    # AI draft content
    draft_content = Column(Text, nullable=True)
    ai_rationale = Column(Text, nullable=True)  # Why AI chose this response
    ai_model = Column(String, nullable=True)  # Which model generated the draft
    generation_latency_ms = Column(Integer, nullable=True)

    # Human actions
    approved_by = Column(String, nullable=True)  # User who approved/rejected
    approval_action = Column(String, nullable=True)  # 'approved', 'rejected', 'edited'
    human_edits = Column(Text, nullable=True)  # Changes made by human
    final_content = Column(Text, nullable=True)  # Final sent content

    # Context used for generation
    order_context = Column(JSON, nullable=True)  # Linked order data used
    conversation_context = Column(JSON, nullable=True)  # Previous messages

    # Performance tracking
    user_satisfaction_score = Column(Integer, nullable=True)  # 1-5 rating if provided
    response_time_improvement = Column(Integer, nullable=True)  # Seconds saved vs manual

    created_at = Column(DateTime, server_default=func.now())

    # Relationships
    email = relationship("Email", back_populates="drafts")

# Mock data models for testing
class MockEmailData:
    """Mock Gmail data for testing without OAuth"""

    @staticmethod
    def get_mock_emails():
        """Return stable mock Gmail threads"""
        return [
            {
                "id": "mock_gmail_1",
                "thread_id": "thread_1",
                "from_email": "customer1@example.com",
                "from_name": "Sarah Johnson",
                "subject": "Question about my custom jewelry order #1234567890",
                "snippet": "Hi! I ordered a custom necklace last week and wanted to check on the status...",
                "body_text": "Hi! I ordered a custom necklace last week (order #1234567890) and wanted to check on the status. Also, would it be possible to change the chain length from 16\" to 18\"? Thank you!",
                "labels": ["INBOX", "UNREAD"],
                "is_unread": True,
                "internal_date": "2024-01-15T10:30:00Z",
                "etsy_receipt_id": "1234567890",
                "has_etsy_links": True,
                "needs_reply": True,
                "reply_priority": "normal",
                "is_refund_related": False
            },
            {
                "id": "mock_gmail_2",
                "thread_id": "thread_2",
                "from_email": "buyer2@gmail.com",
                "from_name": "Mike Chen",
                "subject": "Refund request for damaged item",
                "snippet": "Hello, I received my order yesterday but the ceramic mug arrived cracked...",
                "body_text": "Hello, I received my order yesterday but the ceramic mug arrived cracked. I'd like to request a refund or replacement. The order number is #0987654321. I have photos if needed.",
                "labels": ["INBOX", "IMPORTANT"],
                "is_unread": True,
                "is_important": True,
                "internal_date": "2024-01-14T14:22:00Z",
                "etsy_receipt_id": "0987654321",
                "has_etsy_links": True,
                "needs_reply": True,
                "reply_priority": "high",
                "is_refund_related": True
            },
            {
                "id": "mock_gmail_3",
                "thread_id": "thread_3",
                "from_email": "hello@etsysupport.com",
                "from_name": "Etsy Support",
                "subject": "Your shop's performance this week",
                "snippet": "Here's a summary of your shop's performance for the week ending January 13...",
                "body_text": "Here's a summary of your shop's performance for the week ending January 13. You had 23 views, 3 favorites, and 1 sale. Keep up the great work!",
                "labels": ["INBOX"],
                "is_unread": False,
                "internal_date": "2024-01-13T09:00:00Z",
                "has_etsy_links": False,
                "needs_reply": False,
                "reply_priority": "low"
            },
            {
                "id": "mock_gmail_4",
                "thread_id": "thread_4",
                "from_email": "shipping@etsy.com",
                "from_name": "Etsy Shipping",
                "subject": "Shipping label created for order #1122334455",
                "snippet": "A shipping label has been created for your recent order...",
                "body_text": "A shipping label has been created for your recent order #1122334455. The package should be delivered within 3-5 business days. Tracking: 1Z999999999999999999",
                "labels": ["INBOX"],
                "is_unread": False,
                "internal_date": "2024-01-12T16:45:00Z",
                "etsy_receipt_id": "1122334455",
                "has_etsy_links": True,
                "needs_reply": False,
                "reply_priority": "low"
            },
            {
                "id": "mock_gmail_5",
                "thread_id": "thread_5",
                "from_email": "customer@businessemail.com",
                "from_name": "Lisa Wong",
                "subject": "Bulk order inquiry - wedding favors",
                "snippet": "Hi! I'm planning a wedding and interested in ordering 50 of your handmade soaps...",
                "body_text": "Hi! I'm planning a wedding for September and I'm interested in ordering 50 of your handmade lavender soaps as wedding favors. Could you provide a bulk pricing quote and confirm they can be ready by August 15th? The wedding is on September 2nd. Thank you!",
                "labels": ["INBOX", "UNREAD"],
                "is_unread": True,
                "internal_date": "2024-01-11T11:15:00Z",
                "has_etsy_links": False,
                "needs_reply": True,
                "reply_priority": "high"
            }
        ]

    @staticmethod
    def get_mock_oauth_status():
        """Mock Gmail OAuth connection status"""
        return {
            "connected": True,
            "email": "seller@example.com",
            "provider": "google",
            "last_sync": "2024-01-15T12:00:00Z",
            "messages_count": 5
        }