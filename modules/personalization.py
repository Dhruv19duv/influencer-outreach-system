"""
AI Message Personalization Module
Generates personalized outreach messages using LLM-based prompt engineering.
Supports both email collaboration pitches and Instagram DMs.
"""

import json
import random
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass


@dataclass
class OutreachMessage:
    """A personalized outreach message."""
    influencer_id: str
    influencer_name: str
    platform: str
    email_subject: str
    email_body: str
    dm_message: str
    collaboration_type: str
    personalization_signals: List[str]
    generation_timestamp: str
    message_quality_score: float  # 0-100


class MessagePersonalizer:
    """
    Generates personalized outreach messages using LLM-style prompt engineering.
    Creates both email pitches (60-90 words) and Instagram DMs (15-30 words).
    """

    # Collaboration angles
    COLLABORATIONANGLES = {
        'Sponsorship': {
            'description': 'Paid sponsorship for dedicated content',
            'value_prop': 'we\'d love to partner with you for a sponsored campaign that aligns with your content style',
            'cta': 'Would you be open to discussing a sponsored collaboration?'
        },
        'Affiliate campaign': {
            'description': 'Commission-based affiliate partnership',
            'value_prop': 'we think your audience would love our products, and we\'d love to set you up with an affiliate partnership',
            'cta': 'Interested in joining our affiliate program?'
        },
        'UGC content creation': {
            'description': 'User-generated content creation opportunity',
            'value_prop': 'we\'re looking for authentic creators like you to produce UGC content for our brand',
            'cta': 'Would you be interested in a UGC creation opportunity?'
        },
        'Brand ambassador program': {
            'description': 'Long-term brand ambassador relationship',
            'value_prop': 'we\'re building a community of brand ambassadors and your content perfectly represents what we stand for',
            'cta': 'Would you like to learn more about our ambassador program?'
        },
        'Paid product placement': {
            'description': 'Paid product placement in existing content',
            'value_prop': 'we\'d love to feature our product in your upcoming content through a natural product placement',
            'cta': 'Open to a paid product placement opportunity?'
        },
        'Barter collaboration': {
            'description': 'Product-for-content exchange',
            'value_prop': 'we\'d love to send you our latest collection in exchange for an honest review',
            'cta': 'Would you be interested in a product-for-content collaboration?'
        }
    }

    # Email subject line templates
    EMAIL_SUBJECTS = [
        "Collaboration Opportunity with {brand} - Let's Create Together!",
        "Partnership Inquiry - {brand} x {name}",
        "Exciting Collaboration Opportunity for {name}",
        "{brand} Loves Your Content - Let's Partner!",
        "Exclusive Collaboration Invite for {name}",
        "Your {niche} Content Caught Our Eye - Partnership Opportunity",
        "{brand} x {name} - Potential Collaboration",
        "Let's Create Something Amazing Together, {name}!"
    ]

    # DM templates (short, natural)
    DM_TEMPLATES = [
        "Hey {name}! Love your {theme} content. We have an exciting collab opportunity - interested? 🙌",
        "Hi {name}! Your {niche} content is amazing. Would you be open to a quick chat about a collab?",
        "{name}, your {theme} posts are fire! We'd love to work with you on something cool 🔥",
        "Hey {name}! Big fan of your {niche} content. Got a collab idea - mind if I share?",
        "Hi {name}! Your {theme} content really stands out. Interested in a brand partnership?",
        "{name}! Love what you're doing with {theme}. We have an exciting opportunity for you ✨",
        "Hey {name}! Your {niche} content is exactly what we're looking for. Collab?",
        "Hi {name}! Noticed your amazing {theme} content. Would love to partner up!",
    ]

    def __init__(self, brand_name: str = "StyleCraft", brand_niche: str = "Fashion & Beauty", output_dir: str = 'data'):
        """Initialize the personalizer."""
        self.brand_name = brand_name
        self.brand_niche = brand_niche
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.generated_messages = []
        self.generation_stats = {
            'total_generated': 0,
            'emails_generated': 0,
            'dms_generated': 0,
            'avg_quality_score': 0
        }

    def _build_email_prompt(self, influencer: Dict) -> str:
        """
        Build a prompt for generating personalized email content.
        This simulates LLM prompt engineering.
        """
        prompt = f"""You are a marketing outreach specialist. Generate a personalized collaboration email.

CONTEXT:
- Brand: {self.brand_name}
- Brand Niche: {self.brand_niche}
- Influencer Name: {influencer['name']}
- Influencer Niche: {influencer['niche']}
- Platform: {influencer['platform']}
- Followers: {influencer['followers']:,}
- Engagement Rate: {influencer['engagement_rate']}%
- Content Themes: {', '.join(influencer.get('content_themes', []))}
- Content Tone: {influencer.get('content_tone', 'Professional')}
- Recent Posts: {', '.join(influencer.get('recent_post_topics', [])[:2])}
- Brand Affinities: {', '.join(influencer.get('brand_affinities', []))}
- Classification: {influencer.get('classification', {}).get('tier', 'Standard')}
- Recommended Collaboration: {influencer.get('classification', {}).get('recommended_collaboration', 'Sponsorship')}

REQUIREMENTS:
1. Email length: 60-90 words
2. Reference the influencer's specific content or niche
3. Include a clear value proposition
4. Mention a specific collaboration angle
5. End with a clear call-to-action
6. Be professional but warm
7. Do NOT use generic templates - make it personal

Generate a subject line and email body."""
        return prompt

    def _build_dm_prompt(self, influencer: Dict) -> str:
        """
        Build a prompt for generating personalized DM content.
        """
        prompt = f"""Generate a short, natural Instagram DM for influencer outreach.

CONTEXT:
- Brand: {self.brand_name}
- Influencer: {influencer['name']}
- Niche: {influencer['niche']}
- Key Content Theme: {influencer.get('content_themes', ['content'])[0]}
- Recent Topic: {influencer.get('recent_post_topics', ['posts'])[0] if influencer.get('recent_post_topics') else 'content'}

REQUIREMENTS:
1. DM length: 15-30 words ONLY
2. Be casual and natural (like texting a friend)
3. Reference their specific content
4. Express genuine interest
5. Hint at collaboration without being pushy
6. Use 1-2 emojis max

Generate the DM message."""
        return prompt

    def _generate_email_content(self, influencer: Dict) -> Tuple[str, str]:
        """
        Generate personalized email subject and body.
        Uses prompt-based generation approach.
        """
        name = influencer['name'].split()[0]  # First name
        niche = influencer['niche']
        themes = influencer.get('content_themes', ['content'])
        primary_theme = themes[0] if themes else 'content'
        recent = influencer.get('recent_post_topics', [])
        recent_topic = recent[0] if recent else 'latest content'
        collab_type = influencer.get('classification', {}).get('recommended_collaboration', 'Sponsorship')
        tier = influencer.get('classification', {}).get('tier', 'Standard')

        # Build subject line
        subject = random.choice(self.EMAIL_SUBJECTS).format(
            brand=self.brand_name,
            name=name,
            niche=niche
        )

        # Build email body based on collaboration type and personalization signals
        collab_info = self.COLLABORATIONANGLES.get(collab_type, self.COLLABORATIONANGLES['Sponsorship'])

        # Personalization signals used
        signals = []

        # Greeting
        greeting = f"Hi {name},"

        # Opening - reference their content
        openings = [
            f"I've been following your {niche} content and absolutely loved your recent post about {recent_topic}.",
            f"Your {primary_theme} content really caught my attention - especially your recent take on {recent_topic}.",
            f"I've been enjoying your {niche} content, particularly your {primary_theme} posts.",
            f"Your authentic approach to {niche} content, especially {recent_topic}, really stands out.",
            f"I'm a big fan of your {primary_theme} content and how you engage with your {influencer.get('audience_age', '18-34')} audience."
        ]
        opening = random.choice(openings)
        signals.append(f"Referenced content: {recent_topic}")

        # Value proposition
        value_props = [
            f"At {self.brand_name}, we're passionate about {self.brand_niche.lower()} and believe your content style would be perfect for our brand.",
            f"We're {self.brand_name}, a {self.brand_niche.lower()} brand, and we think your {primary_theme} content aligns perfectly with our vision.",
            f"As a {self.brand_niche.lower()} brand, we've been looking for creators who genuinely understand their audience - and you do.",
            f"We believe your {niche} expertise and engaged community would love what we're building at {self.brand_name}."
        ]
        value_prop = random.choice(value_props)
        signals.append(f"Value prop: {collab_info['description']}")

        # Collaboration pitch
        collab_pitches = [
            f"{collab_info['value_prop'].capitalize()}, and we think it would be a natural fit for your audience.",
            f"We'd love to {collab_info['value_prop']}.",
            f"I think a {collab_type.lower()} would be mutually beneficial - {collab_info['value_prop']}."
        ]
        collab_pitch = random.choice(collab_pitches)
        signals.append(f"Collaboration type: {collab_type}")

        # CTA
        cta = collab_info['cta']

        # Assemble email (target 60-90 words)
        email_body = f"{greeting}\n\n{opening}\n\n{value_prop}\n\n{collab_pitch}\n\n{cta}\n\nLooking forward to hearing from you!\n\nBest,\nThe {self.brand_name} Team"

        # Count words and adjust if needed
        word_count = len(email_body.split())
        if word_count > 90:
            # Trim to fit
            sentences = email_body.split('\n\n')
            if len(sentences) > 4:
                email_body = '\n\n'.join(sentences[:5])

        return subject, email_body

    def _generate_dm_content(self, influencer: Dict) -> str:
        """
        Generate personalized Instagram DM (15-30 words).
        """
        name = influencer['name'].split()[0]
        niche = influencer['niche']
        themes = influencer.get('content_themes', ['content'])
        primary_theme = themes[0] if themes else 'content'

        template = random.choice(self.DM_TEMPLATES)
        dm = template.format(
            name=name,
            niche=niche,
            theme=primary_theme
        )

        # Ensure DM is within 15-30 words
        words = dm.split()
        if len(words) > 30:
            dm = ' '.join(words[:30])
        elif len(words) < 15:
            dm += " Let me know! 😊"

        return dm

    def _calculate_quality_score(self, influencer: Dict, email: str, dm: str) -> float:
        """Calculate a quality score for generated messages."""
        score = 50  # Base score

        # Personalization signals
        name = influencer['name'].split()[0]
        if name in email:
            score += 10
        if name in dm:
            score += 5

        # Niche reference
        if influencer['niche'].lower() in email.lower():
            score += 10
        if influencer['niche'].lower() in dm.lower():
            score += 5

        # Content theme reference
        themes = influencer.get('content_themes', [])
        for theme in themes:
            if theme.lower() in email.lower():
                score += 5
                break

        # Length compliance
        email_words = len(email.split())
        if 60 <= email_words <= 90:
            score += 10
        elif 50 <= email_words <= 100:
            score += 5

        dm_words = len(dm.split())
        if 15 <= dm_words <= 30:
            score += 10
        elif 10 <= dm_words <= 35:
            score += 5

        return min(score, 100)

    def personalize_influencer(self, influencer: Dict) -> OutreachMessage:
        """
        Generate personalized outreach messages for a single influencer.
        """
        # Generate email
        email_subject, email_body = self._generate_email_content(influencer)

        # Generate DM
        dm_message = self._generate_dm_content(influencer)

        # Calculate quality
        quality = self._calculate_quality_score(influencer, email_body, dm_message)

        # Identify personalization signals used
        signals = []
        signals.append(f"Referenced niche: {influencer['niche']}")
        signals.append(f"Referenced content themes: {', '.join(influencer.get('content_themes', [])[:2])}")
        if influencer.get('recent_post_topics'):
            signals.append(f"Referenced recent content: {influencer['recent_post_topics'][0]}")
        signals.append(f"Collaboration type: {influencer.get('classification', {}).get('recommended_collaboration', 'Sponsorship')}")

        message = OutreachMessage(
            influencer_id=influencer.get('username', ''),
            influencer_name=influencer['name'],
            platform=influencer['platform'],
            email_subject=email_subject,
            email_body=email_body,
            dm_message=dm_message,
            collaboration_type=influencer.get('classification', {}).get('recommended_collaboration', 'Sponsorship'),
            personalization_signals=signals,
            generation_timestamp=datetime.now().isoformat(),
            message_quality_score=quality
        )

        # Update stats
        self.generation_stats['total_generated'] += 1
        self.generation_stats['emails_generated'] += 1
        self.generation_stats['dms_generated'] += 1

        return message

    def personalize_all(self, influencers: List[Dict]) -> List[OutreachMessage]:
        """
        Generate personalized messages for all influencers.
        """
        print(f"\n✨ Generating personalized messages for {len(influencers)} influencers...")

        messages = []
        for i, inf in enumerate(influencers, 1):
            msg = self.personalize_influencer(inf)
            messages.append(msg)

            if i % 10 == 0:
                print(f"   📊 Progress: {i}/{len(influencers)} messages generated")

        self.generated_messages = messages

        # Calculate average quality
        if messages:
            avg_quality = sum(m.message_quality_score for m in messages) / len(messages)
            self.generation_stats['avg_quality_score'] = round(avg_quality, 1)

        # Print summary
        print(f"\n✅ Message Generation Complete!")
        print(f"   📧 Emails generated: {self.generation_stats['emails_generated']}")
        print(f"   💬 DMs generated: {self.generation_stats['dms_generated']}")
        print(f"   ⭐ Average quality score: {self.generation_stats['avg_quality_score']}/100")

        return messages

    def get_prompt_examples(self, count: int = 3) -> List[Dict]:
        """
        Get example prompts used for message generation.
        Useful for documentation and demonstrating LLM integration.
        """
        examples = []
        sample_influencers = random.sample(
            self.generated_messages,
            k=min(count, len(self.generated_messages))
        )

        for msg in sample_influencers:
            # Build a simplified influencer dict for prompt generation
            simple_influencer = {
                'name': msg.influencer_name,
                'username': msg.influencer_id,
                'niche': msg.collaboration_type,
                'platform': msg.platform,
                'followers': 25000,
                'engagement_rate': 4.5,
                'content_themes': [s.split(': ')[1] if ': ' in s else s for s in msg.personalization_signals[:2]],
                'recent_post_topics': ['Recent content'],
                'audience_age': '18-34',
                'content_tone': 'Professional',
                'brand_affinities': ['Fashion & Apparel'],
                'classification': {
                    'tier': 'Premium',
                    'recommended_collaboration': msg.collaboration_type
                }
            }
            examples.append({
                'influencer': msg.influencer_name,
                'email_prompt': self._build_email_prompt(simple_influencer),
                'dm_prompt': self._build_dm_prompt(simple_influencer),
                'generated_email_subject': msg.email_subject,
                'generated_email_body': msg.email_body,
                'generated_dm': msg.dm_message
            })

        return examples

    def save_messages(self, filename: str = 'personalized_messages.json') -> str:
        """Save generated messages to JSON."""
        filepath = self.output_dir / filename

        output = {
            'metadata': {
                'total_messages': len(self.generated_messages),
                'generation_stats': self.generation_stats,
                'brand_name': self.brand_name,
                'brand_niche': self.brand_niche,
                'generation_timestamp': datetime.now().isoformat()
            },
            'messages': [
                {
                    'influencer_id': msg.influencer_id,
                    'influencer_name': msg.influencer_name,
                    'platform': msg.platform,
                    'email_subject': msg.email_subject,
                    'email_body': msg.email_body,
                    'dm_message': msg.dm_message,
                    'collaboration_type': msg.collaboration_type,
                    'personalization_signals': msg.personalization_signals,
                    'quality_score': msg.message_quality_score,
                    'timestamp': msg.generation_timestamp
                }
                for msg in self.generated_messages
            ]
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"💾 Messages saved to: {filepath}")
        return str(filepath)

    def save_messages_csv(self, filename: str = 'personalized_messages.csv') -> str:
        """Save messages as CSV."""
        filepath = self.output_dir / filename

        import csv
        csv_data = []
        for msg in self.generated_messages:
            csv_data.append({
                'Influencer Name': msg.influencer_name,
                'Platform': msg.platform,
                'Collaboration Type': msg.collaboration_type,
                'Email Subject': msg.email_subject,
                'Email Body': msg.email_body,
                'DM Message': msg.dm_message,
                'Quality Score': msg.message_quality_score,
                'Personalization Signals': ' | '.join(msg.personalization_signals),
                'Generated At': msg.generation_timestamp
            })

        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
                writer.writeheader()
                writer.writerows(csv_data)

        print(f"📄 Messages saved to CSV: {filepath}")
        return str(filepath)
