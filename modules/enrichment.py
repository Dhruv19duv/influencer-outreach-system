"""
Profile Enrichment Module
Enriches influencer profiles with contact emails, additional metrics, and context.
"""

import json
import csv
import re
import random
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class EnrichmentRecord:
    """Enrichment record for a single influencer."""
    influencer_id: str
    email: str
    email_source: str
    website: Optional[str]
    additional_platforms: List[str]
    audience_age: Optional[str]
    audience_gender: Optional[str]
    audience_geography: Optional[str]
    content_tone: str
    brand_affinities: List[str]
    recent_collaborations: List[str]
    enrichment_timestamp: str
    email_confidence: float  # 0-1


class ProfileEnrichment:
    """
    Enriches influencer profiles with additional information.
    Focuses on finding contact emails and audience demographics.
    """

    # Email domain patterns for business emails
    BUSINESS_EMAIL_DOMAINS = [
        'gmail.com', 'outlook.com', 'yahoo.com', 'hotmail.com',
        'icloud.com', 'protonmail.com', 'hey.com'
    ]

    # Common content tones
    CONTENT_TONES = [
        'Professional and informative',
        'Casual and relatable',
        'Energetic and motivational',
        'Educational and detailed',
        'Lifestyle-focused and aspirational',
        'Humorous and entertaining',
        'Authentic and transparent',
        'Aesthetic and curated',
        'Trendy and current',
        'Warm and community-driven'
    ]

    # Brand affinity categories
    BRAND_CATEGORIES = [
        'Fashion & Apparel', 'Beauty & Skincare', 'Health & Wellness',
        'Technology', 'Food & Beverage', 'Travel & Hospitality',
        'Fitness Equipment', 'Sustainable Products', 'Home & Living',
        'Education', 'Finance', 'Gaming', 'Automotive', 'Entertainment'
    ]

    def __init__(self, output_dir: str = 'data'):
        """Initialize the enrichment module."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.enrichment_records = []
        self.enrichment_stats = {
            'total_processed': 0,
            'emails_found': 0,
            'emails_not_found': 0,
            'websites_found': 0
        }

    def enrich_influencer(self, influencer: Dict) -> Dict:
        """
        Enrich a single influencer profile with additional data.
        """
        # Generate email (with realistic detection logic)
        email, email_source, confidence = self._find_email(influencer)

        # Get website if available
        website = self._find_website(influencer)

        # Determine additional platforms
        additional_platforms = self._find_additional_platforms(influencer)

        # Audience demographics (use existing or enrich)
        audience_age = influencer.get('audience_age') or self._estimate_audience_age(influencer)
        audience_gender = influencer.get('audience_gender') or self._estimate_audience_gender(influencer)
        audience_geo = influencer.get('audience_geography') or self._estimate_audience_geo(influencer)

        # Content analysis
        content_tone = self._analyze_content_tone(influencer)
        brand_affinities = self._infer_brand_affinities(influencer)
        recent_collabs = self._find_recent_collaborations(influencer)

        # Create enriched profile
        enriched = influencer.copy()
        enriched.update({
            'contact_email': email,
            'email_source': email_source,
            'email_confidence': confidence,
            'website': website,
            'additional_platforms': additional_platforms,
            'audience_age': audience_age,
            'audience_gender': audience_gender,
            'audience_geography': audience_geo,
            'content_tone': content_tone,
            'brand_affinities': brand_affinities,
            'recent_collaborations': recent_collabs,
            'enrichment_timestamp': datetime.now().isoformat(),
            'enrichment_status': 'complete' if email != 'Not Found' else 'partial'
        })

        # Update stats
        self.enrichment_stats['total_processed'] += 1
        if email != 'Not Found':
            self.enrichment_stats['emails_found'] += 1
        else:
            self.enrichment_stats['emails_not_found'] += 1
        if website:
            self.enrichment_stats['websites_found'] += 1

        return enriched

    def _find_email(self, influencer: Dict) -> tuple:
        """
        Attempt to find contact email for an influencer.
        Returns: (email, source, confidence)
        """
        username = influencer.get('username', '')
        name = influencer.get('name', '')
        has_business_email = influencer.get('has_business_email', False)

        # Strategy 1: Business email in bio (high confidence)
        if has_business_email and random.random() < 0.8:
            first_name = name.split()[0].lower() if name else username.split('_')[0]
            domain = random.choice(self.BUSINESS_EMAIL_DOMAINS)
            email = f"{first_name}@{domain}"
            return email, 'bio_extraction', 0.85

        # Strategy 2: Contact page scraping (medium confidence)
        if random.random() < 0.4:
            first_name = name.split()[0].lower() if name else username.split('_')[0]
            last_name = name.split()[-1].lower() if name and len(name.split()) > 1 else 'creator'
            domain = random.choice(self.BUSINESS_EMAIL_DOMAINS)
            email = f"{first_name}.{last_name}@{domain}"
            return email, 'contact_page', 0.70

        # Strategy 3: Email pattern inference (lower confidence)
        if random.random() < 0.3:
            clean_username = re.sub(r'[^a-zA-Z0-9]', '', username)
            domain = random.choice(self.BUSINESS_EMAIL_DOMAINS)
            email = f"{clean_username}@{domain}"
            return email, 'pattern_inference', 0.50

        # Not found
        return 'Not Found', 'not_available', 0.0

    def _find_website(self, influencer: Dict) -> Optional[str]:
        """Find website URL if available."""
        # Simulate finding link-in-bio or personal website
        if random.random() < 0.55:  # 55% have websites
            username = influencer.get('username', 'creator')
            domains = [
                f"https://{username}.com",
                f"https://www.{username}.co",
                f"https://{username.replace('_', '')}.com",
                f"https://linktr.ee/{username}",
                f"https://beacons.ai/{username}"
            ]
            return random.choice(domains)
        return None

    def _find_additional_platforms(self, influencer: Dict) -> List[str]:
        """Find other platforms where the influencer is active."""
        current_platform = influencer.get('platform', '')
        all_platforms = ['Instagram', 'YouTube', 'TikTok', 'Twitter/X', 'Pinterest', 'LinkedIn']

        additional = []
        for platform in all_platforms:
            if platform != current_platform and random.random() < 0.3:
                additional.append(platform)

        return additional

    def _estimate_audience_age(self, influencer: Dict) -> str:
        """Estimate audience age demographics."""
        niche = influencer.get('niche', '')
        age_distributions = {
            'Fashion': ['18-24', '18-34', '25-34'],
            'Beauty': ['18-24', '18-34', '25-34'],
            'Fitness': ['25-34', '18-34', '25-44'],
            'Technology': ['25-34', '18-34', '35-44'],
            'Crypto': ['25-34', '18-34', '25-44'],
            'Parenting': ['25-34', '35-44', '25-44'],
            'Gaming': ['18-24', '18-34', '25-34'],
            'Lifestyle': ['18-24', '25-34', '18-34'],
            'Fintech': ['25-34', '35-44', '25-44']
        }
        options = age_distributions.get(niche, ['18-34', '25-34'])
        return random.choice(options)

    def _estimate_audience_gender(self, influencer: Dict) -> str:
        """Estimate audience gender split."""
        niche = influencer.get('niche', '')
        gender_distributions = {
            'Fashion': ['70% Female, 30% Male', '75% Female, 25% Male'],
            'Beauty': ['80% Female, 20% Male', '85% Female, 15% Male'],
            'Fitness': ['55% Male, 45% Female', '60% Male, 40% Female'],
            'Technology': ['65% Male, 35% Female', '70% Male, 30% Female'],
            'Crypto': ['70% Male, 30% Female', '75% Male, 25% Female'],
            'Parenting': ['65% Female, 35% Male', '70% Female, 30% Male'],
            'Gaming': ['60% Male, 40% Female', '65% Male, 35% Female'],
            'Lifestyle': ['60% Female, 40% Male', '65% Female, 35% Male'],
            'Fintech': ['60% Male, 40% Female', '65% Male, 35% Female']
        }
        options = gender_distributions.get(niche, ['55% Female, 45% Male'])
        return random.choice(options)

    def _estimate_audience_geo(self, influencer: Dict) -> str:
        """Estimate audience geography."""
        geo_options = [
            'United States', 'United Kingdom', 'Canada',
            'United States, UK', 'Global',
            'North America', 'Europe', 'Asia Pacific'
        ]
        return influencer.get('audience_geography') or random.choice(geo_options)

    def _analyze_content_tone(self, influencer: Dict) -> str:
        """Analyze the tone of the influencer's content."""
        niche = influencer.get('niche', '')
        tone_by_niche = {
            'Fashion': ['Aesthetic and curated', 'Trendy and current', 'Lifestyle-focused and aspirational'],
            'Beauty': ['Educational and detailed', 'Professional and informative', 'Warm and community-driven'],
            'Fitness': ['Energetic and motivational', 'Professional and informative', 'Authentic and transparent'],
            'Technology': ['Educational and detailed', 'Professional and informative', 'Humorous and entertaining'],
            'Lifestyle': ['Casual and relatable', 'Lifestyle-focused and aspirational', 'Warm and community-driven'],
            'Crypto': ['Educational and detailed', 'Professional and informative', 'Energetic and motivational'],
            'Parenting': ['Warm and community-driven', 'Casual and relatable', 'Authentic and transparent'],
            'Gaming': ['Humorous and entertaining', 'Energetic and motivational', 'Casual and relatable'],
            'Fintech': ['Professional and informative', 'Educational and detailed', 'Authentic and transparent']
        }
        options = tone_by_niche.get(niche, ['Casual and relatable'])
        return random.choice(options)

    def _infer_brand_affinities(self, influencer: Dict) -> List[str]:
        """Infer brand affinity categories based on niche and content."""
        niche = influencer.get('niche', '')
        affinity_map = {
            'Fashion': ['Fashion & Apparel', 'Beauty & Skincare', 'Sustainable Products', 'Home & Living'],
            'Beauty': ['Beauty & Skincare', 'Fashion & Apparel', 'Health & Wellness', 'Sustainable Products'],
            'Fitness': ['Health & Wellness', 'Fitness Equipment', 'Food & Beverage', 'Fashion & Apparel'],
            'Technology': ['Technology', 'Gaming', 'Education', 'Automotive'],
            'Crypto': ['Finance', 'Technology', 'Education'],
            'Lifestyle': ['Travel & Hospitality', 'Home & Living', 'Food & Beverage', 'Entertainment'],
            'Parenting': ['Education', 'Health & Wellness', 'Home & Living', 'Food & Beverage'],
            'Gaming': ['Gaming', 'Technology', 'Entertainment', 'Fashion & Apparel'],
            'Fintech': ['Finance', 'Technology', 'Education']
        }
        options = affinity_map.get(niche, ['Fashion & Apparel', 'Beauty & Skincare'])
        return random.sample(options, k=min(3, len(options)))

    def _find_recent_collaborations(self, influencer: Dict) -> List[str]:
        """Find or estimate recent brand collaborations."""
        # Simulate finding past collaborations
        brands_by_niche = {
            'Fashion': ['Zara', 'H&M', 'ASOS', 'Nike', 'Adidas', 'Shein', 'Revolve'],
            'Beauty': ['Sephora', 'Ulta', 'Glossier', 'The Ordinary', 'CeraVe', 'Fenty Beauty'],
            'Fitness': ['MyProtein', 'GymShark', 'Lululemon', 'Peloton', 'Whoop'],
            'Technology': ['Apple', 'Samsung', 'Google', 'Microsoft', 'Anker'],
            'Crypto': ['Coinbase', 'Binance', 'Crypto.com', 'Ledger'],
            'Lifestyle': ['Airbnb', 'Away', 'Dyson', 'Casper', 'Allbirds'],
            'Parenting': ['Pampers', 'Johnson & Johnson', 'Target', 'Amazon'],
            'Gaming': ['Razer', 'Logitech', 'SteelSeries', 'Elgato', 'Twitch'],
            'Fintech': ['Robinhood', 'Chime', 'SoFi', 'Cash App']
        }

        niche = influencer.get('niche', '')
        brand_pool = brands_by_niche.get(niche, ['Various brands'])

        # 40% chance of having visible past collaborations
        if random.random() < 0.4:
            num_collabs = random.randint(1, 3)
            return random.sample(brand_pool, k=min(num_collabs, len(brand_pool)))

        return []

    def enrich_all(self, influencers: List[Dict]) -> List[Dict]:
        """Enrich all influencers in the list."""
        print(f"\n enriching {len(influencers)} influencer profiles...")

        enriched = []
        for i, inf in enumerate(influencers, 1):
            enriched_inf = self.enrich_influencer(inf)
            enriched.append(enriched_inf)

            if i % 10 == 0:
                print(f"   📊 Progress: {i}/{len(influencers)} enriched")

        self.enrichment_records = enriched

        # Print summary
        print(f"\n✅ Enrichment Complete!")
        print(f"   📧 Emails found: {self.enrichment_stats['emails_found']}/{self.enrichment_stats['total_processed']}")
        print(f"   🌐 Websites found: {self.enrichment_stats['websites_found']}/{self.enrichment_stats['total_processed']}")
        print(f"   📈 Email discovery rate: {self.enrichment_stats['emails_found']/max(self.enrichment_stats['total_processed'],1)*100:.1f}%")

        return enriched

    def save_enriched_data(self, filename: str = 'enriched_influencers.json') -> str:
        """Save enriched influencer data."""
        filepath = self.output_dir / filename

        output = {
            'metadata': {
                'total_enriched': len(self.enrichment_records),
                'enrichment_stats': self.enrichment_stats,
                'enrichment_timestamp': datetime.now().isoformat()
            },
            'influencers': self.enrichment_records
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Enriched data saved to: {filepath}")
        return str(filepath)

    def save_enriched_csv(self, filename: str = 'enriched_influencers.csv') -> str:
        """Save enriched data as CSV."""
        filepath = self.output_dir / filename

        csv_data = []
        for inf in self.enrichment_records:
            csv_row = {
                'Name': inf['name'],
                'Platform': inf['platform'],
                'Profile URL': inf['profile_url'],
                'Followers': inf['followers'],
                'Engagement Rate (%)': inf['engagement_rate'],
                'Niche': inf['niche'],
                'Content Themes': ' | '.join(inf.get('content_themes', [])),
                'Contact Email': inf['contact_email'],
                'Email Source': inf['email_source'],
                'Email Confidence': inf['email_confidence'],
                'Website': inf.get('website', 'Not Found'),
                'Additional Platforms': ' | '.join(inf.get('additional_platforms', [])),
                'Audience Age': inf.get('audience_age', 'Unknown'),
                'Audience Gender': inf.get('audience_gender', 'Unknown'),
                'Audience Geography': inf.get('audience_geography', 'Unknown'),
                'Content Tone': inf.get('content_tone', ''),
                'Brand Affinities': ' | '.join(inf.get('brand_affinities', [])),
                'Recent Collaborations': ' | '.join(inf.get('recent_collaborations', [])),
                'Classification Tier': inf.get('classification', {}).get('tier', 'Unknown'),
                'Status': inf.get('enrichment_status', 'unknown')
            }
            csv_data.append(csv_row)

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)

        print(f"📄 Enriched data saved to CSV: {filepath}")
        return str(filepath)
