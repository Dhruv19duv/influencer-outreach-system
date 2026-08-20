"""
Influencer Filtering & Classification Module
Filters and classifies influencers based on predefined criteria.
"""

from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path
from datetime import datetime


class FilterStatus(Enum):
    PASSED = "passed"
    FAILED = "failed"
    CONDITIONAL = "conditional"


@dataclass
class FilterResult:
    """Result of applying a filter to an influencer."""
    filter_name: str
    status: FilterStatus
    score: float  # 0-100
    reason: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ClassificationResult:
    """Classification result for an influencer."""
    tier: str  # 'Premium', 'Standard', 'Budget', 'Rejected'
    category: str
    brand_fit_score: float
    recommended_collaboration: str
    reasoning: str


class InfluencerFilter:
    """
    Filters and classifies influencers based on multiple criteria.
    """

    # Configuration
    MIN_FOLLOWERS = 5000
    MAX_FOLLOWERS = 100000
    MIN_ENGAGEMENT_RATE = 1.5
    MAX_ENGAGEMENT_RATE = 10.0
    MIN_POSTS_PER_WEEK = 2

    # Brand fit criteria (can be customized)
    PREFERRED_NICHES = ['Fashion', 'Beauty', 'Lifestyle']
    PREFERRED_PLATFORMS = ['Instagram', 'YouTube']
    PREFERRED_REGIONS = ['United States', 'United Kingdom', 'Canada', 'Australia', 'Europe', 'North America']

    # Collaboration types
    COLLABORATION_TYPES = [
        'Sponsorship', 'Affiliate campaign', 'UGC content creation',
        'Brand ambassador program', 'Paid product placement', 'Barter collaboration'
    ]

    def __init__(self, output_dir: str = 'data'):
        """Initialize the filter."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.filter_results = {}
        self.classification_results = {}
        self.passed_influencers = []
        self.failed_influencers = []

    def filter_by_followers(self, influencer: Dict) -> FilterResult:
        """Filter by follower count range."""
        followers = influencer['followers']

        if self.MIN_FOLLOWERS <= followers <= self.MAX_FOLLOWERS:
            score = 100
            if followers < 15000:
                score = 80  # Smaller but still valid
                status = FilterStatus.PASSED
                reason = f"Micro-influencer with {followers:,} followers (small tier)"
            elif followers < 50000:
                score = 90
                status = FilterStatus.PASSED
                reason = f"Mid-range micro-influencer with {followers:,} followers"
            else:
                score = 95
                status = FilterStatus.PASSED
                reason = f"Large micro-influencer with {followers:,} followers"
        elif followers < self.MIN_FOLLOWERS:
            score = 20
            status = FilterStatus.FAILED
            reason = f"Below minimum threshold ({followers:,} < {self.MIN_FOLLOWERS:,})"
        else:
            score = 40
            status = FilterStatus.CONDITIONAL
            reason = f"Above micro-influencer range ({followers:,}) - may be macro"

        return FilterResult(
            filter_name='followers',
            status=status,
            score=score,
            reason=reason,
            details={'followers': followers, 'min': self.MIN_FOLLOWERS, 'max': self.MAX_FOLLOWERS}
        )

    def filter_by_engagement(self, influencer: Dict) -> FilterResult:
        """Filter by engagement rate."""
        engagement = influencer['engagement_rate']

        if self.MIN_ENGAGEMENT_RATE <= engagement <= self.MAX_ENGAGEMENT_RATE:
            if engagement >= 4.0:
                score = 100
                reason = f"Excellent engagement rate: {engagement}%"
            elif engagement >= 2.5:
                score = 85
                reason = f"Good engagement rate: {engagement}%"
            else:
                score = 70
                reason = f"Acceptable engagement rate: {engagement}%"
            status = FilterStatus.PASSED
        elif engagement < self.MIN_ENGAGEMENT_RATE:
            score = 15
            status = FilterStatus.FAILED
            reason = f"Low engagement rate: {engagement}% (minimum: {self.MIN_ENGAGEMENT_RATE}%)"
        else:
            score = 60
            status = FilterStatus.CONDITIONAL
            reason = f"Very high engagement: {engagement}% - verify authenticity"

        return FilterResult(
            filter_name='engagement',
            status=status,
            score=score,
            reason=reason,
            details={'engagement_rate': engagement}
        )

    def filter_by_niche(self, influencer: Dict) -> FilterResult:
        """Filter by niche/category relevance."""
        niche = influencer['niche']

        if niche in self.PREFERRED_NICHES:
            score = 100
            status = FilterStatus.PASSED
            reason = f"High-priority niche: {niche}"
        elif niche in ['Fitness', 'Lifestyle', 'Technology']:
            score = 75
            status = FilterStatus.PASSED
            reason = f"Relevant niche: {niche}"
        else:
            score = 50
            status = FilterStatus.CONDITIONAL
            reason = f"Secondary niche: {niche} - may still be viable"

        return FilterResult(
            filter_name='niche',
            status=status,
            score=score,
            reason=reason,
            details={'niche': niche, 'preferred': self.PREFERRED_NICHES}
        )

    def filter_by_platform(self, influencer: Dict) -> FilterResult:
        """Filter by platform preference."""
        platform = influencer['platform']

        if platform in self.PREFERRED_PLATFORMS:
            score = 100
            status = FilterStatus.PASSED
            reason = f"Preferred platform: {platform}"
        elif platform == 'TikTok':
            score = 80
            status = FilterStatus.PASSED
            reason = f"Growing platform: {platform}"
        else:
            score = 60
            status = FilterStatus.CONDITIONAL
            reason = f"Non-preferred platform: {platform}"

        return FilterResult(
            filter_name='platform',
            status=status,
            score=score,
            reason=reason,
            details={'platform': platform}
        )

    def filter_by_content_quality(self, influencer: Dict) -> FilterResult:
        """Filter based on content quality indicators."""
        posts_per_week = influencer.get('posts_per_week', 0)
        verified = influencer.get('verified', False)
        themes = influencer.get('content_themes', [])

        score = 50  # Base score

        # Posting frequency
        if posts_per_week >= 5:
            score += 20
        elif posts_per_week >= 3:
            score += 10

        # Verification bonus
        if verified:
            score += 15

        # Content theme diversity
        if len(themes) >= 3:
            score += 15

        score = min(score, 100)

        if score >= 70:
            status = FilterStatus.PASSED
            reason = f"Good content quality indicators (score: {score})"
        elif score >= 50:
            status = FilterStatus.CONDITIONAL
            reason = f"Adequate content quality (score: {score})"
        else:
            status = FilterStatus.FAILED
            reason = f"Low content quality indicators (score: {score})"

        return FilterResult(
            filter_name='content_quality',
            status=status,
            score=score,
            reason=reason,
            details={
                'posts_per_week': posts_per_week,
                'verified': verified,
                'theme_count': len(themes)
            }
        )

    def filter_by_audience_fit(self, influencer: Dict) -> FilterResult:
        """Filter by audience demographics fit."""
        geo = influencer.get('audience_geography', '')
        age = influencer.get('audience_age', '')

        score = 50

        # Geographic fit
        if geo in self.PREFERRED_REGIONS:
            score += 25
        elif geo == 'Global':
            score += 15

        # Age demographic fit (18-44 is typically valuable)
        if age in ['18-34', '25-44', '18-24', '25-34']:
            score += 25
        elif age == '35-44':
            score += 20

        score = min(score, 100)

        if score >= 70:
            status = FilterStatus.PASSED
            reason = f"Strong audience fit (geo: {geo}, age: {age})"
        elif score >= 50:
            status = FilterStatus.CONDITIONAL
            reason = f"Moderate audience fit (geo: {geo}, age: {age})"
        else:
            status = FilterStatus.FAILED
            reason = f"Poor audience fit (geo: {geo}, age: {age})"

        return FilterResult(
            filter_name='audience_fit',
            status=status,
            score=score,
            reason=reason,
            details={'geography': geo, 'age': age}
        )

    def filter_influencer(self, influencer: Dict) -> Tuple[bool, Dict, ClassificationResult]:
        """
        Apply all filters to a single influencer.
        Returns: (passed, filter_results, classification)
        """
        results = {}

        # Apply all filters
        results['followers'] = self.filter_by_followers(influencer)
        results['engagement'] = self.filter_by_engagement(influencer)
        results['niche'] = self.filter_by_niche(influencer)
        results['platform'] = self.filter_by_platform(influencer)
        results['content_quality'] = self.filter_by_content_quality(influencer)
        results['audience_fit'] = self.filter_by_audience_fit(influencer)

        # Calculate overall score
        scores = [r.score for r in results.values()]
        overall_score = sum(scores) / len(scores)

        # Determine pass/fail
        failed_filters = [r for r in results.values() if r.status == FilterStatus.FAILED]
        passed = len(failed_filters) <= 1 and overall_score >= 55

        # Classify the influencer
        classification = self._classify_influencer(influencer, overall_score, results)

        return passed, results, classification

    def _classify_influencer(
        self, influencer: Dict, overall_score: float, filter_results: Dict
    ) -> ClassificationResult:
        """Classify influencer into tiers and recommend collaboration type."""

        # Tier classification
        if overall_score >= 85:
            tier = 'Premium'
        elif overall_score >= 70:
            tier = 'Standard'
        elif overall_score >= 55:
            tier = 'Budget'
        else:
            tier = 'Rejected'

        # Category
        category = influencer['niche']

        # Brand fit score (0-100)
        brand_fit = round(overall_score, 1)

        # Recommended collaboration type
        followers = influencer['followers']
        engagement = influencer['engagement_rate']

        if followers > 50000 and engagement > 3.0:
            collab = 'Sponsorship'
        elif engagement > 5.0:
            collab = 'UGC content creation'
        elif followers > 30000:
            collab = 'Brand ambassador program'
        elif engagement > 4.0:
            collab = 'Affiliate campaign'
        else:
            collab = 'Barter collaboration'

        # Reasoning
        reasoning = f"Overall score: {overall_score:.1f}/100. "
        if tier == 'Premium':
            reasoning += "High-value influencer with strong metrics across all criteria. "
        elif tier == 'Standard':
            reasoning += "Solid influencer with good potential for collaboration. "
        else:
            reasoning += "Meets minimum criteria but may need additional vetting. "

        reasoning += f"Recommended approach: {collab}."

        return ClassificationResult(
            tier=tier,
            category=category,
            brand_fit_score=brand_fit,
            recommended_collaboration=collab,
            reasoning=reasoning
        )

    def filter_all(self, influencers: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Filter all influencers and return passed/failed lists.
        """
        print(f"\n🔍 Filtering {len(influencers)} influencers...")

        passed = []
        failed = []

        for inf in influencers:
            did_pass, results, classification = self.filter_influencer(inf)

            inf['filter_results'] = {k: {
                'status': v.status.value,
                'score': v.score,
                'reason': v.reason
            } for k, v in results.items()}

            inf['classification'] = {
                'tier': classification.tier,
                'category': classification.category,
                'brand_fit_score': classification.brand_fit_score,
                'recommended_collaboration': classification.recommended_collaboration,
                'reasoning': classification.reasoning
            }

            if did_pass:
                passed.append(inf)
            else:
                failed.append(inf)

        self.passed_influencers = passed
        self.failed_influencers = failed

        # Summary
        print(f"\n📊 Filtering Results:")
        print(f"   ✅ Passed: {len(passed)}")
        print(f"   ❌ Failed: {len(failed)}")
        print(f"   📈 Pass Rate: {len(passed)/len(influencers)*100:.1f}%")

        # Tier breakdown
        tiers = {}
        for inf in passed:
            tier = inf['classification']['tier']
            tiers[tier] = tiers.get(tier, 0) + 1
        print(f"   🏆 Tier Breakdown: {tiers}")

        return passed, failed

    def save_results(self, filename: str = 'filtering_results.json') -> str:
        """Save filtering results."""
        filepath = self.output_dir / filename

        output = {
            'metadata': {
                'total_processed': len(self.passed_influencers) + len(self.failed_influencers),
                'passed': len(self.passed_influencers),
                'failed': len(self.failed_influencers),
                'filter_timestamp': datetime.now().isoformat(),
                'filter_config': {
                    'min_followers': self.MIN_FOLLOWERS,
                    'max_followers': self.MAX_FOLLOWERS,
                    'min_engagement': self.MIN_ENGAGEMENT_RATE,
                    'preferred_niches': self.PREFERRED_NICHES,
                    'preferred_platforms': self.PREFERRED_PLATFORMS
                }
            },
            'passed_influencers': self.passed_influencers,
            'failed_influencers': [
                {
                    'name': inf['name'],
                    'username': inf['username'],
                    'platform': inf['platform'],
                    'followers': inf['followers'],
                    'niche': inf['niche'],
                    'filter_results': inf.get('filter_results', {}),
                    'reason_for_failure': self._get_failure_reason(inf)
                }
                for inf in self.failed_influencers
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Filtering results saved to: {filepath}")
        return str(filepath)

    def _get_failure_reason(self, influencer: Dict) -> str:
        """Get the primary reason for filtering failure."""
        filter_results = influencer.get('filter_results', {})
        failed_filters = [
            f"{k}: {v['reason']}"
            for k, v in filter_results.items()
            if v.get('status') == 'failed'
        ]
        return '; '.join(failed_filters) if failed_filters else 'Overall score below threshold'

    def get_filter_summary(self) -> Dict:
        """Get a summary of filtering results."""
        return {
            'total_processed': len(self.passed_influencers) + len(self.failed_influencers),
            'passed': len(self.passed_influencers),
            'failed': len(self.failed_influencers),
            'pass_rate': round(
                len(self.passed_influencers) / max(len(self.passed_influencers) + len(self.failed_influencers), 1) * 100, 1
            ),
            'tiers': {
                tier: sum(1 for i in self.passed_influencers if i['classification']['tier'] == tier)
                for tier in ['Premium', 'Standard', 'Budget']
            }
        }
