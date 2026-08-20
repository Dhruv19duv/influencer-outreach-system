#!/usr/bin/env python3
"""
Automated Micro-Influencer Outreach System
Main Pipeline Orchestrator

Workflow: Discovery → Filtering → Enrichment → Personalization → Sending → Tracking

Author: EDXSO AI Engineer Intern Assignment
Date: August 2026
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.discovery import InfluencerDiscovery
from modules.filtering import InfluencerFilter
from modules.enrichment import ProfileEnrichment
from modules.personalization import MessagePersonalizer
from modules.sending import EmailSender, DMSender
from modules.tracker import OutreachTracker


def print_banner():
    """Print the system banner."""
    banner = """
╔══════════════════════════════════════════════════════════════════════╗
║         🚀 AUTOMATED MICRO-INFLUENCER OUTREACH SYSTEM 🚀           ║
║                  EDXSO AI Engineer Intern Assignment                ║
╠══════════════════════════════════════════════════════════════════════╣
║  Pipeline: Discovery → Filtering → Enrichment → Personalization     ║
║            → Sending → Tracking                                     ║
╚══════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_pipeline(
    niche: str = 'Fashion',
    min_influencers: int = 50,
    brand_name: str = 'StyleCraft',
    brand_niche: str = 'Fashion & Beauty',
    simulation_mode: bool = True,
    output_dir: str = 'data'
):
    """
    Run the complete influencer outreach pipeline.

    Args:
        niche: Target niche for influencer discovery
        min_influencers: Minimum number of influencers to discover
        brand_name: Your brand name
        brand_niche: Your brand's niche
        simulation_mode: Whether to simulate sending (True) or actually send (False)
        output_dir: Directory for output files
    """
    print_banner()
    start_time = datetime.now()

    print(f"📋 Configuration:")
    print(f"   Target Niche: {niche}")
    print(f"   Min Influencers: {min_influencers}")
    print(f"   Brand: {brand_name}")
    print(f"   Brand Niche: {brand_niche}")
    print(f"   Mode: {'Simulation' if simulation_mode else 'Live'}")
    print(f"   Output Dir: {output_dir}")
    print()

    # ============================================================
    # PHASE 1: INFLUENCER DISCOVERY
    # ============================================================
    print("=" * 70)
    print("PHASE 1: INFLUENCER DISCOVERY")
    print("=" * 70)

    discovery = InfluencerDiscovery(output_dir=output_dir)
    influencers = discovery.discover_all(target_niche=niche, min_influencers=min_influencers)

    # Save discovery data
    discovery.save_discovery()
    discovery.save_as_csv()

    # Print discovery stats
    stats = discovery.get_stats()
    print(f"\n📊 Discovery Statistics:")
    print(f"   Total: {stats['total_discovered']}")
    print(f"   By Platform: {stats['by_platform']}")
    print(f"   Avg Followers: {stats['avg_followers']:,}")
    print(f"   Avg Engagement: {stats['avg_engagement']}%")

    # ============================================================
    # PHASE 2: FILTERING & CLASSIFICATION
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 2: FILTERING & CLASSIFICATION")
    print("=" * 70)

    filter_module = InfluencerFilter(output_dir=output_dir)
    passed_influencers, failed_influencers = filter_module.filter_all(influencers)

    # Save filter results
    filter_module.save_results()

    # Print filter summary
    filter_summary = filter_module.get_filter_summary()
    print(f"\n📊 Filter Summary:")
    print(f"   Pass Rate: {filter_summary['pass_rate']}%")
    print(f"   Tiers: {filter_summary['tiers']}")

    # ============================================================
    # PHASE 3: PROFILE ENRICHMENT
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 3: PROFILE ENRICHMENT")
    print("=" * 70)

    enrichment = ProfileEnrichment(output_dir=output_dir)
    enriched_influencers = enrichment.enrich_all(passed_influencers)

    # Save enriched data
    enrichment.save_enriched_data()
    enrichment.save_enriched_csv()

    # ============================================================
    # PHASE 4: AI MESSAGE PERSONALIZATION
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 4: AI MESSAGE PERSONALIZATION")
    print("=" * 70)

    personalizer = MessagePersonalizer(
        brand_name=brand_name,
        brand_niche=brand_niche,
        output_dir=output_dir
    )
    messages = personalizer.personalize_all(enriched_influencers)

    # Save messages
    personalizer.save_messages()
    personalizer.save_messages_csv()

    # Show sample prompts
    prompt_examples = personalizer.get_prompt_examples(count=2)
    print(f"\n📝 Sample LLM Prompts Used:")
    for i, ex in enumerate(prompt_examples, 1):
        print(f"\n   Example {i} - {ex['influencer']}:")
        print(f"   Generated Email Subject: {ex['generated_email_subject']}")
        print(f"   Generated DM: {ex['generated_dm'][:80]}...")

    # ============================================================
    # PHASE 5: SENDING LAYER
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 5: SENDING LAYER")
    print("=" * 70)

    # Email sending
    email_sender = EmailSender(output_dir=output_dir, simulation_mode=simulation_mode)

    # Prepare message dicts for sending
    message_dicts = [
        {
            'email_subject': msg.email_subject,
            'email_body': msg.email_body,
            'dm_message': msg.dm_message
        }
        for msg in messages
    ]

    email_results = email_sender.send_batch(enriched_influencers, message_dicts)
    email_sender.save_send_log()

    # DM sending
    dm_sender = DMSender(output_dir=output_dir)
    dm_results = dm_sender.send_batch_dm(enriched_influencers, message_dicts)
    dm_sender.save_dm_log()

    # ============================================================
    # PHASE 6: OUTREACH TRACKING
    # ============================================================
    print("\n" + "=" * 70)
    print("PHASE 6: OUTREACH TRACKING")
    print("=" * 70)

    tracker = OutreachTracker(output_dir=output_dir)

    # Convert results to dicts for tracker
    email_result_dicts = [
        {
            'status': r.status,
            'message_id': r.message_id,
            'error': r.error
        }
        for r in email_results
    ]

    dm_result_dicts = [
        {
            'status': r.status,
            'message_id': r.message_id
        }
        for r in dm_results
    ]

    tracker.add_records_batch(
        enriched_influencers,
        message_dicts,
        email_result_dicts,
        dm_result_dicts
    )

    # Save tracker
    tracker.save_tracker()
    tracker.save_tracker_csv()
    tracker.print_tracker_table()

    # Print final summary
    summary = tracker.get_tracker_summary()

    elapsed_time = (datetime.now() - start_time).total_seconds()

    print("\n" + "=" * 70)
    print("🎉 PIPELINE COMPLETE!")
    print("=" * 70)
    print(f"\n⏱️  Total Time: {elapsed_time:.2f} seconds")
    print(f"\n📊 Final Summary:")
    print(f"   Total Influencers Discovered: {stats['total_discovered']}")
    print(f"   Passed Filtering: {filter_summary['passed']}")
    print(f"   Enriched: {len(enriched_influencers)}")
    print(f"   Messages Generated: {len(messages)}")
    print(f"   Emails Sent/Simulated: {summary['overview']['emails_sent']}")
    print(f"   DMs Queued: {summary['overview']['dms_queued']}")
    print(f"\n📁 Output Files:")
    print(f"   📄 data/discovered_influencers.json")
    print(f"   📄 data/discovered_influencers.csv")
    print(f"   📄 data/filtering_results.json")
    print(f"   📄 data/enriched_influencers.json")
    print(f"   📄 data/enriched_influencers.csv")
    print(f"   📄 data/personalized_messages.json")
    print(f"   📄 data/personalized_messages.csv")
    print(f"   📄 data/email_send_log.json")
    print(f"   📄 data/dm_send_log.json")
    print(f"   📄 data/outreach_tracker.json")
    print(f"   📄 data/outreach_tracker.csv")

    return {
        'discovery': stats,
        'filtering': filter_summary,
        'enrichment': enrichment.enrichment_stats,
        'personalization': personalizer.generation_stats,
        'sending': email_sender.stats,
        'tracking': summary,
        'elapsed_time': elapsed_time
    }


def demo_mode():
    """Run a quick demo with sample data."""
    print("\n🎮 Running in DEMO mode with sample data...\n")

    return run_pipeline(
        niche='Fashion',
        min_influencers=55,
        brand_name='StyleCraft',
        brand_niche='Fashion & Beauty',
        simulation_mode=True,
        output_dir='data'
    )


def full_mode():
    """Run the full pipeline."""
    print("\n🚀 Running FULL pipeline...\n")

    return run_pipeline(
        niche='Fashion',
        min_influencers=55,
        brand_name='StyleCraft',
        brand_niche='Fashion & Beauty',
        simulation_mode=True,
        output_dir='data'
    )


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Automated Micro-Influencer Outreach System')
    parser.add_argument('--mode', choices=['demo', 'full'], default='demo',
                       help='Run mode: demo (quick test) or full (complete pipeline)')
    parser.add_argument('--niche', default='Fashion',
                       help='Target niche (default: Fashion)')
    parser.add_argument('--count', type=int, default=55,
                       help='Minimum number of influencers (default: 55)')
    parser.add_argument('--brand', default='StyleCraft',
                       help='Brand name (default: StyleCraft)')
    parser.add_argument('--live', action='store_true',
                       help='Run in live mode (actually sends emails)')

    args = parser.parse_args()

    if args.mode == 'demo':
        demo_mode()
    else:
        run_pipeline(
            niche=args.niche,
            min_influencers=args.count,
            brand_name=args.brand,
            brand_niche='Fashion & Beauty',
            simulation_mode=not args.live,
            output_dir='data'
        )
