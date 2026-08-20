"""
Outreach Tracker Module
Tracks all outreach activities including emails, DMs, and responses.
"""

import json
import csv
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class OutreachRecord:
    """A single outreach record."""
    influencer_name: str
    influencer_username: str
    platform: str
    email: str
    profile_url: str
    followers: int
    engagement_rate: float
    niche: str
    classification_tier: str
    email_subject: str
    email_message: str
    dm_message: str
    email_sent: bool
    dm_queued: bool
    email_status: str  # 'sent', 'simulated', 'failed', 'pending'
    dm_status: str  # 'queued', 'sent', 'pending'
    send_date: str
    response_status: str  # 'pending', 'replied', 'interested', 'declined'
    notes: str


class OutreachTracker:
    """
    Tracks all outreach activities and maintains a comprehensive log.
    """

    def __init__(self, output_dir: str = 'data'):
        """Initialize the tracker."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.records: List[OutreachRecord] = []
        self.tracking_stats = {
            'total_outreach': 0,
            'emails_sent': 0,
            'dms_queued': 0,
            'pending_responses': 0,
            'responses_received': 0,
            'interested': 0,
            'declined': 0
        }

    def add_record(
        self,
        influencer: Dict,
        message: Dict,
        email_result: Optional[Dict] = None,
        dm_result: Optional[Dict] = None
    ) -> OutreachRecord:
        """
        Add an outreach record for an influencer.
        """
        # Determine email status
        email_status = 'pending'
        email_sent = False
        if email_result:
            email_status = email_result.get('status', 'pending')
            email_sent = email_status in ['sent', 'simulated']

        # Determine DM status
        dm_status = 'pending'
        dm_queued = False
        if dm_result:
            dm_status = dm_result.get('status', 'pending')
            dm_queued = dm_status in ['simulated', 'queued']

        record = OutreachRecord(
            influencer_name=influencer.get('name', ''),
            influencer_username=influencer.get('username', ''),
            platform=influencer.get('platform', ''),
            email=influencer.get('contact_email', 'Not Found'),
            profile_url=influencer.get('profile_url', ''),
            followers=influencer.get('followers', 0),
            engagement_rate=influencer.get('engagement_rate', 0),
            niche=influencer.get('niche', ''),
            classification_tier=influencer.get('classification', {}).get('tier', 'Unknown'),
            email_subject=message.get('email_subject', ''),
            email_message=message.get('email_body', ''),
            dm_message=message.get('dm_message', ''),
            email_sent=email_sent,
            dm_queued=dm_queued,
            email_status=email_status,
            dm_status=dm_status,
            send_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            response_status='pending',
            notes=''
        )

        self.records.append(record)
        self._update_stats()
        return record

    def add_records_batch(
        self,
        influencers: List[Dict],
        messages: List[Dict],
        email_results: Optional[List[Dict]] = None,
        dm_results: Optional[List[Dict]] = None
    ) -> List[OutreachRecord]:
        """
        Add multiple outreach records at once.
        """
        records = []
        for i, (inf, msg) in enumerate(zip(influencers, messages)):
            email_result = email_results[i] if email_results and i < len(email_results) else None
            dm_result = dm_results[i] if dm_results and i < len(dm_results) else None

            record = self.add_record(inf, msg, email_result, dm_result)
            records.append(record)

        return records

    def _update_stats(self):
        """Update tracking statistics."""
        self.tracking_stats['total_outreach'] = len(self.records)
        self.tracking_stats['emails_sent'] = sum(
            1 for r in self.records if r.email_sent
        )
        self.tracking_stats['dms_queued'] = sum(
            1 for r in self.records if r.dm_queued
        )
        self.tracking_stats['pending_responses'] = sum(
            1 for r in self.records if r.response_status == 'pending'
        )
        self.tracking_stats['responses_received'] = sum(
            1 for r in self.records if r.response_status != 'pending'
        )
        self.tracking_stats['interested'] = sum(
            1 for r in self.records if r.response_status == 'interested'
        )
        self.tracking_stats['declined'] = sum(
            1 for r in self.records if r.response_status == 'declined'
        )

    def update_response_status(
        self,
        influencer_username: str,
        status: str,
        notes: str = ''
    ):
        """
        Update the response status for an influencer.
        Status options: 'pending', 'replied', 'interested', 'declined'
        """
        for record in self.records:
            if record.influencer_username == influencer_username:
                record.response_status = status
                if notes:
                    record.notes = notes
                self._update_stats()
                return

    def get_tracker_summary(self) -> Dict:
        """Get a comprehensive summary of outreach activities."""
        # Platform breakdown
        platform_stats = {}
        for r in self.records:
            platform_stats[r.platform] = platform_stats.get(r.platform, 0) + 1

        # Niche breakdown
        niche_stats = {}
        for r in self.records:
            niche_stats[r.niche] = niche_stats.get(r.niche, 0) + 1

        # Tier breakdown
        tier_stats = {}
        for r in self.records:
            tier_stats[r.classification_tier] = tier_stats.get(r.classification_tier, 0) + 1

        # Engagement metrics
        total_followers = sum(r.followers for r in self.records)
        avg_engagement = sum(r.engagement_rate for r in self.records) / max(len(self.records), 1)

        return {
            'overview': self.tracking_stats,
            'by_platform': platform_stats,
            'by_niche': niche_stats,
            'by_tier': tier_stats,
            'total_followers_reached': total_followers,
            'average_engagement_rate': round(avg_engagement, 2),
            'response_rate': round(
                self.tracking_stats['responses_received'] / max(self.tracking_stats['total_outreach'], 1) * 100, 1
            ),
            'interest_rate': round(
                self.tracking_stats['interested'] / max(self.tracking_stats['responses_received'], 1) * 100, 1
            ) if self.tracking_stats['responses_received'] > 0 else 0
        }

    def save_tracker(self, filename: str = 'outreach_tracker.json') -> str:
        """Save the outreach tracker to JSON."""
        filepath = self.output_dir / filename

        output = {
            'metadata': {
                'total_records': len(self.records),
                'tracking_stats': self.tracking_stats,
                'summary': self.get_tracker_summary(),
                'save_timestamp': datetime.now().isoformat()
            },
            'records': [
                {
                    'influencer_name': r.influencer_name,
                    'influencer_username': r.influencer_username,
                    'platform': r.platform,
                    'email': r.email,
                    'profile_url': r.profile_url,
                    'followers': r.followers,
                    'engagement_rate': r.engagement_rate,
                    'niche': r.niche,
                    'classification_tier': r.classification_tier,
                    'email_subject': r.email_subject,
                    'email_message': r.email_message,
                    'dm_message': r.dm_message,
                    'email_sent': r.email_sent,
                    'dm_queued': r.dm_queued,
                    'email_status': r.email_status,
                    'dm_status': r.dm_status,
                    'send_date': r.send_date,
                    'response_status': r.response_status,
                    'notes': r.notes
                }
                for r in self.records
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Outreach tracker saved to: {filepath}")
        return str(filepath)

    def save_tracker_csv(self, filename: str = 'outreach_tracker.csv') -> str:
        """Save the outreach tracker as CSV."""
        filepath = self.output_dir / filename

        csv_data = []
        for r in self.records:
            csv_data.append({
                'Influencer Name': r.influencer_name,
                'Username': r.influencer_username,
                'Platform': r.platform,
                'Email': r.email,
                'Profile URL': r.profile_url,
                'Followers': r.followers,
                'Engagement Rate (%)': r.engagement_rate,
                'Niche': r.niche,
                'Classification Tier': r.classification_tier,
                'Email Subject': r.email_subject,
                'Email Message': r.email_message[:100] + '...' if len(r.email_message) > 100 else r.email_message,
                'DM Message': r.dm_message,
                'Email Sent': 'Yes' if r.email_sent else 'No',
                'DM Queued': 'Yes' if r.dm_queued else 'No',
                'Email Status': r.email_status,
                'DM Status': r.dm_status,
                'Send Date': r.send_date,
                'Response Status': r.response_status,
                'Notes': r.notes
            })

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)

        print(f"📄 Outreach tracker saved to CSV: {filepath}")
        return str(filepath)

    def print_tracker_table(self):
        """Print a formatted table of outreach records."""
        if not self.records:
            print("No outreach records found.")
            return

        print("\n" + "=" * 120)
        print("OUTREACH TRACKER")
        print("=" * 120)

        header = f"{'Name':<20} {'Platform':<12} {'Followers':<12} {'Email Status':<12} {'DM Status':<10} {'Response':<12}"
        print(header)
        print("-" * 120)

        for r in self.records:
            row = (
                f"{r.influencer_name[:18]:<20} "
                f"{r.platform:<12} "
                f"{r.followers:<12,} "
                f"{r.email_status:<12} "
                f"{r.dm_status:<10} "
                f"{r.response_status:<12}"
            )
            print(row)

        print("=" * 120)
        print(f"\nTotal: {len(self.records)} records")
        print(f"Emails Sent/Simulated: {self.tracking_stats['emails_sent']}")
        print(f"DMs Queued: {self.tracking_stats['dms_queued']}")
