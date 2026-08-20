"""
Sending Layer Module
Demonstrates email and DM sending with simulation and logging.
Supports Gmail API, SMTP, and manual workflows.
"""

import json
import csv
import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, field


@dataclass
class SendResult:
    """Result of a send attempt."""
    influencer_id: str
    influencer_name: str
    email: str
    message_type: str  # 'email' or 'dm'
    status: str  # 'sent', 'simulated', 'failed', 'skipped'
    error: Optional[str] = None
    timestamp: str = ''
    message_id: Optional[str] = None


class EmailSender:
    """
    Email sending layer with multiple delivery methods.
    Supports simulation mode for demo purposes.
    """

    def __init__(self, output_dir: str = 'data', simulation_mode: bool = True):
        """
        Initialize the email sender.

        Args:
            output_dir: Directory for logs and output
            simulation_mode: If True, simulates sending without actual delivery
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.simulation_mode = simulation_mode
        self.send_log = []
        self.sent_emails = set()  # Prevent duplicates
        self.stats = {
            'total_attempted': 0,
            'sent': 0,
            'simulated': 0,
            'failed': 0,
            'skipped': 0,
            'duplicates_prevented': 0
        }

    def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        influencer_id: str,
        influencer_name: str
    ) -> SendResult:
        """
        Send or simulate sending an email.

        Args:
            to_email: Recipient email address
            subject: Email subject line
            body: Email body content
            influencer_id: Unique identifier for the influencer
            influencer_name: Name for logging

        Returns:
            SendResult with status and details
        """
        self.stats['total_attempted'] += 1

        # Check for valid email
        if not to_email or to_email == 'Not Found':
            self.stats['skipped'] += 1
            result = SendResult(
                influencer_id=influencer_id,
                influencer_name=influencer_name,
                email=to_email or 'N/A',
                message_type='email',
                status='skipped',
                error='No valid email address',
                timestamp=datetime.now().isoformat()
            )
            self.send_log.append(result)
            return result

        # Prevent duplicate outreach
        if influencer_id in self.sent_emails:
            self.stats['duplicates_prevented'] += 1
            result = SendResult(
                influencer_id=influencer_id,
                influencer_name=influencer_name,
                email=to_email,
                message_type='email',
                status='skipped',
                error='Duplicate outreach prevented',
                timestamp=datetime.now().isoformat()
            )
            self.send_log.append(result)
            return result

        # Mark as sent to prevent duplicates
        self.sent_emails.add(influencer_id)

        if self.simulation_mode:
            return self._simulate_send(to_email, subject, body, influencer_id, influencer_name)
        else:
            return self._actual_send(to_email, subject, body, influencer_id, influencer_name)

    def _simulate_send(
        self,
        to_email: str,
        subject: str,
        body: str,
        influencer_id: str,
        influencer_name: str
    ) -> SendResult:
        """Simulate email sending for demo purposes."""
        # Simulate success/failure
        success = random.random() < 0.95  # 95% success rate

        if success:
            message_id = f"sim_{influencer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            self.stats['simulated'] += 1

            result = SendResult(
                influencer_id=influencer_id,
                influencer_name=influencer_name,
                email=to_email,
                message_type='email',
                status='simulated',
                timestamp=datetime.now().isoformat(),
                message_id=message_id
            )
        else:
            self.stats['failed'] += 1
            result = SendResult(
                influencer_id=influencer_id,
                influencer_name=influencer_name,
                email=to_email,
                message_type='email',
                status='failed',
                error='Simulated delivery failure',
                timestamp=datetime.now().isoformat()
            )

        self.send_log.append(result)
        return result

    def _actual_send(
        self,
        to_email: str,
        subject: str,
        body: str,
        influencer_id: str,
        influencer_name: str
    ) -> SendResult:
        """
        Actually send an email via SMTP.
        Requires SMTP configuration in environment variables.
        """
        try:
            import os
            smtp_host = os.getenv('SMTP_HOST', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER', '')
            smtp_pass = os.getenv('SMTP_PASS', '')

            if not smtp_user or not smtp_pass:
                raise ValueError("SMTP credentials not configured")

            # Create message
            msg = MIMEMultipart()
            msg['From'] = smtp_user
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Send
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_pass)
                server.send_message(msg)

            self.stats['sent'] += 1
            message_id = f"real_{influencer_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}"

            result = SendResult(
                influencer_id=influencer_id,
                influencer_name=influencer_name,
                email=to_email,
                message_type='email',
                status='sent',
                timestamp=datetime.now().isoformat(),
                message_id=message_id
            )

        except Exception as e:
            self.stats['failed'] += 1
            result = SendResult(
                influencer_id=influencer_id,
                influencer_name=influencer_name,
                email=to_email,
                message_type='email',
                status='failed',
                error=str(e),
                timestamp=datetime.now().isoformat()
            )

        self.send_log.append(result)
        return result

    def send_batch(
        self,
        influencers: List[Dict],
        messages: List[Dict]
    ) -> List[SendResult]:
        """
        Send emails to a batch of influencers.

        Args:
            influencers: List of enriched influencer dicts
            messages: List of message dicts (must match influencers order)

        Returns:
            List of SendResult objects
        """
        print(f"\n📧 Processing email batch for {len(influencers)} influencers...")
        print(f"   Mode: {'Simulation' if self.simulation_mode else 'Live'}")

        results = []
        for i, (inf, msg) in enumerate(zip(influencers, messages), 1):
            result = self.send_email(
                to_email=inf.get('contact_email', 'Not Found'),
                subject=msg.get('email_subject', ''),
                body=msg.get('email_body', ''),
                influencer_id=inf.get('username', ''),
                influencer_name=inf.get('name', '')
            )
            results.append(result)

            if i % 10 == 0:
                print(f"   📊 Progress: {i}/{len(influencers)} emails processed")

        print(f"\n✅ Email batch complete!")
        print(f"   📨 Sent/Simulated: {self.stats['sent'] + self.stats['simulated']}")
        print(f"   ⚠️  Failed: {self.stats['failed']}")
        print(f"   ⏭️  Skipped: {self.stats['skipped']}")
        print(f"   🔄 Duplicates prevented: {self.stats['duplicates_prevented']}")

        return results

    def save_send_log(self, filename: str = 'email_send_log.json') -> str:
        """Save the send log to file."""
        filepath = self.output_dir / filename

        output = {
            'metadata': {
                'total_attempted': self.stats['total_attempted'],
                'stats': self.stats,
                'simulation_mode': self.simulation_mode,
                'log_timestamp': datetime.now().isoformat()
            },
            'send_log': [
                {
                    'influencer_id': r.influencer_id,
                    'influencer_name': r.influencer_name,
                    'email': r.email,
                    'message_type': r.message_type,
                    'status': r.status,
                    'error': r.error,
                    'timestamp': r.timestamp,
                    'message_id': r.message_id
                }
                for r in self.send_log
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Email send log saved to: {filepath}")
        return str(filepath)


class DMSender:
    """
    Instagram/DM sending layer with simulation.
    Demonstrates how DM outreach would work.
    """

    def __init__(self, output_dir: str = 'data'):
        """Initialize the DM sender."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.dm_log = []
        self.sent_dms = set()  # Prevent duplicates
        self.stats = {
            'total_attempted': 0,
            'simulated': 0,
            'manual_queue': 0,
            'duplicates_prevented': 0
        }

    def send_dm(
        self,
        influencer_id: str,
        influencer_name: str,
        platform: str,
        dm_message: str,
        profile_url: str
    ) -> SendResult:
        """
        Simulate or queue a DM for manual sending.

        Note: Direct automated DM sending is restricted by most platforms.
        This module demonstrates the workflow and queues messages for manual sending.
        """
        self.stats['total_attempted'] += 1

        # Prevent duplicates
        if influencer_id in self.sent_dms:
            self.stats['duplicates_prevented'] += 1
            return SendResult(
                influencer_id=influencer_id,
                influencer_name=influencer_name,
                email='N/A',
                message_type='dm',
                status='skipped',
                error='Duplicate DM prevented',
                timestamp=datetime.now().isoformat()
            )

        self.sent_dms.add(influencer_id)

        # DMs are always queued for manual sending (platform restriction)
        self.stats['manual_queue'] += 1

        result = SendResult(
            influencer_id=influencer_id,
            influencer_name=influencer_name,
            email='N/A',
            message_type='dm',
            status='simulated',
            timestamp=datetime.now().isoformat(),
            message_id=f"dm_queue_{influencer_id}"
        )

        self.dm_log.append({
            'influencer_id': influencer_id,
            'influencer_name': influencer_name,
            'platform': platform,
            'dm_message': dm_message,
            'profile_url': profile_url,
            'status': 'queued_for_manual_send',
            'timestamp': datetime.now().isoformat()
        })

        return result

    def send_batch_dm(
        self,
        influencers: List[Dict],
        messages: List[Dict]
    ) -> List[SendResult]:
        """
        Queue DMs for a batch of influencers.
        """
        print(f"\n💬 Processing DM batch for {len(influencers)} influencers...")
        print(f"   ℹ️  DMs will be queued for manual sending (platform restriction)")

        results = []
        for inf, msg in zip(influencers, messages):
            result = self.send_dm(
                influencer_id=inf.get('username', ''),
                influencer_name=inf.get('name', ''),
                platform=inf.get('platform', ''),
                dm_message=msg.get('dm_message', ''),
                profile_url=inf.get('profile_url', '')
            )
            results.append(result)

        print(f"\n✅ DM batch complete!")
        print(f"   📬 Queued for manual sending: {self.stats['manual_queue']}")
        print(f"   🔄 Duplicates prevented: {self.stats['duplicates_prevented']}")

        return results

    def save_dm_log(self, filename: str = 'dm_send_log.json') -> str:
        """Save the DM send log."""
        filepath = self.output_dir / filename

        output = {
            'metadata': {
                'total_attempted': self.stats['total_attempted'],
                'stats': self.stats,
                'note': 'DMs are queued for manual sending due to platform restrictions',
                'log_timestamp': datetime.now().isoformat()
            },
            'dm_queue': self.dm_log
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 DM log saved to: {filepath}")
        return str(filepath)
