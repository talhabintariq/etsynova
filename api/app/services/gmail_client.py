import os
import re
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google.auth.credentials import Credentials
from google.auth.transport.requests import Request as GoogleRequest
from google_auth_oauthlib.flow import Flow
from app.models.inbox import MockEmailData
import base64
import email
from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

class GmailClient:
    """Gmail API client for fetching and managing emails"""

    def __init__(self, credentials: Optional[Credentials] = None):
        self.credentials = credentials
        self.service = None
        self.mock_mode = os.getenv("MOCK_MODE", "false") == "true"

        if not self.mock_mode and credentials:
            self.service = build('gmail', 'v1', credentials=credentials)

    def _refresh_credentials(self) -> bool:
        """Refresh expired credentials"""
        if not self.credentials:
            return False

        try:
            if self.credentials.expired and self.credentials.refresh_token:
                self.credentials.refresh(GoogleRequest())
                return True
        except Exception as e:
            logger.error(f"Failed to refresh credentials: {e}")
            return False

        return True

    async def sync_messages(self, max_results: int = 50) -> Dict:
        """Fetch and sync last N messages from Gmail"""
        if self.mock_mode:
            return {
                "messages": MockEmailData.get_mock_emails(),
                "total": 5,
                "synced": 5,
                "last_sync": datetime.utcnow().isoformat()
            }

        if not self.service or not self._refresh_credentials():
            raise Exception("Gmail service not authenticated")

        try:
            # Get message list
            results = self.service.users().messages().list(
                userId='me',
                maxResults=max_results,
                q='in:inbox'  # Only inbox messages
            ).execute()

            messages = results.get('messages', [])
            synced_messages = []

            for msg in messages:
                try:
                    # Get full message details
                    message = self.service.users().messages().get(
                        userId='me',
                        id=msg['id'],
                        format='full'
                    ).execute()

                    parsed_message = self._parse_gmail_message(message)
                    if parsed_message:
                        synced_messages.append(parsed_message)

                except Exception as e:
                    logger.error(f"Failed to fetch message {msg['id']}: {e}")
                    continue

            return {
                "messages": synced_messages,
                "total": len(messages),
                "synced": len(synced_messages),
                "last_sync": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Gmail sync failed: {e}")
            raise Exception(f"Failed to sync Gmail messages: {str(e)}")

    def _parse_gmail_message(self, message: Dict) -> Optional[Dict]:
        """Parse Gmail API message into our format"""
        try:
            headers = {h['name']: h['value'] for h in message['payload']['headers']}

            # Extract body content
            body_text = ""
            body_html = ""

            if 'parts' in message['payload']:
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                        body_text = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                    elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                        body_html = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'data' in message['payload']['body']:
                body_text = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8')

            # Convert internal date to datetime
            internal_date = datetime.fromtimestamp(int(message['internalDate']) / 1000)

            # Detect Etsy links and order numbers
            etsy_receipt_id, has_etsy_links = self._detect_etsy_links(
                subject=headers.get('Subject', ''),
                body=body_text
            )

            # Determine if needs reply (basic heuristics)
            needs_reply = self._needs_reply_heuristic(
                from_email=headers.get('From', ''),
                subject=headers.get('Subject', ''),
                body=body_text,
                labels=message.get('labelIds', [])
            )

            # Check if refund-related
            is_refund_related = self._is_refund_related(
                subject=headers.get('Subject', ''),
                body=body_text
            )

            # Calculate retention policy
            retention_until = self._calculate_retention_date(
                internal_date=internal_date,
                is_linked_to_order=bool(etsy_receipt_id)
            )

            return {
                "message_id": message['id'],
                "thread_id": message['threadId'],
                "from_email": self._extract_email_from_header(headers.get('From', '')),
                "from_name": self._extract_name_from_header(headers.get('From', '')),
                "to_emails": [headers.get('To', '')],  # Simplified for now
                "subject": headers.get('Subject', ''),
                "snippet": message.get('snippet', ''),
                "body_text": body_text,
                "body_html": body_html,
                "labels": message.get('labelIds', []),
                "is_unread": 'UNREAD' in message.get('labelIds', []),
                "is_important": 'IMPORTANT' in message.get('labelIds', []),
                "internal_date": internal_date.isoformat(),
                "etsy_receipt_id": etsy_receipt_id,
                "has_etsy_links": has_etsy_links,
                "needs_reply": needs_reply,
                "reply_priority": self._calculate_priority(
                    is_important='IMPORTANT' in message.get('labelIds', []),
                    is_refund=is_refund_related,
                    from_domain=self._extract_domain_from_email(headers.get('From', ''))
                ),
                "is_refund_related": is_refund_related,
                "retention_until": retention_until.isoformat() if retention_until else None,
                "is_linked_to_order": bool(etsy_receipt_id)
            }

        except Exception as e:
            logger.error(f"Failed to parse message: {e}")
            return None

    def _detect_etsy_links(self, subject: str, body: str) -> tuple[Optional[str], bool]:
        """Detect Etsy order numbers and links in email content"""
        combined_text = f"{subject} {body}".lower()

        # Patterns for Etsy order numbers
        order_patterns = [
            r'order #?(\d{10,})',
            r'receipt #?(\d{10,})',
            r'etsy\.com/your/shops/[^/]+/transactions/(\d+)',
            r'transaction[:\s]+(\d{10,})'
        ]

        # Check for order numbers
        for pattern in order_patterns:
            match = re.search(pattern, combined_text)
            if match:
                return match.group(1), True

        # Check for general Etsy links
        etsy_patterns = [
            r'etsy\.com',
            r'@etsy',
            r'etsy support',
            r'etsy seller',
            r'your etsy shop'
        ]

        has_etsy_links = any(re.search(pattern, combined_text) for pattern in etsy_patterns)
        return None, has_etsy_links

    def _needs_reply_heuristic(self, from_email: str, subject: str, body: str, labels: List[str]) -> bool:
        """Determine if email likely needs a reply using basic heuristics"""

        # Skip auto-generated emails
        auto_senders = ['noreply', 'no-reply', 'donotreply', 'support@etsy.com', 'shipping@etsy.com']
        if any(sender in from_email.lower() for sender in auto_senders):
            return False

        # Check for question indicators
        question_indicators = [
            'question', '?', 'help', 'how', 'when', 'where', 'why', 'what',
            'can you', 'could you', 'would you', 'please', 'custom', 'bulk order',
            'refund', 'return', 'exchange', 'problem', 'issue', 'concern'
        ]

        combined_text = f"{subject} {body}".lower()
        has_question = any(indicator in combined_text for indicator in question_indicators)

        # If already replied to, probably doesn't need reply
        if 'SENT' in labels:
            return False

        return has_question and 'UNREAD' in labels

    def _is_refund_related(self, subject: str, body: str) -> bool:
        """Check if email is related to refunds or returns"""
        refund_keywords = [
            'refund', 'return', 'exchange', 'damaged', 'defective',
            'broken', 'wrong item', 'not as described', 'cancel order',
            'dispute', 'chargeback', 'money back'
        ]

        combined_text = f"{subject} {body}".lower()
        return any(keyword in combined_text for keyword in refund_keywords)

    def _calculate_priority(self, is_important: bool, is_refund: bool, from_domain: str) -> str:
        """Calculate reply priority based on various factors"""
        if is_refund:
            return 'high'
        if is_important:
            return 'high'
        if 'gmail.com' in from_domain or 'yahoo.com' in from_domain:
            return 'normal'
        # Business emails might be higher priority
        if not any(provider in from_domain for provider in ['gmail.com', 'yahoo.com', 'hotmail.com']):
            return 'high'
        return 'normal'

    def _calculate_retention_date(self, internal_date: datetime, is_linked_to_order: bool) -> Optional[datetime]:
        """Calculate when email should be deleted based on retention policy"""
        retention_days = int(os.getenv('EMAIL_RETENTION_DAYS', '90'))

        # If linked to order, keep longer or indefinitely
        if is_linked_to_order:
            order_retention_days = int(os.getenv('ORDER_EMAIL_RETENTION_DAYS', '365'))
            return internal_date + timedelta(days=order_retention_days)

        return internal_date + timedelta(days=retention_days)

    def _extract_email_from_header(self, header: str) -> str:
        """Extract email address from From/To header"""
        if '<' in header and '>' in header:
            match = re.search(r'<([^>]+)>', header)
            return match.group(1) if match else header
        return header.strip()

    def _extract_name_from_header(self, header: str) -> Optional[str]:
        """Extract display name from From header"""
        if '<' in header:
            name_part = header.split('<')[0].strip()
            return name_part.strip('"') if name_part else None
        return None

    def _extract_domain_from_email(self, email_addr: str) -> str:
        """Extract domain from email address"""
        if '@' in email_addr:
            return email_addr.split('@')[-1].lower()
        return ''

    async def get_message_by_id(self, message_id: str) -> Optional[Dict]:
        """Get a specific message by ID"""
        if self.mock_mode:
            mock_emails = MockEmailData.get_mock_emails()
            for email in mock_emails:
                if email['id'] == message_id:
                    return email
            return None

        if not self.service or not self._refresh_credentials():
            raise Exception("Gmail service not authenticated")

        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()

            return self._parse_gmail_message(message)

        except Exception as e:
            logger.error(f"Failed to get message {message_id}: {e}")
            return None

    async def mark_as_read(self, message_id: str) -> bool:
        """Mark message as read"""
        if self.mock_mode:
            return True  # Simulate success

        if not self.service or not self._refresh_credentials():
            return False

        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            return True

        except Exception as e:
            logger.error(f"Failed to mark message as read: {e}")
            return False