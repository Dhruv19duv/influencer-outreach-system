# 🚀 Automated Micro-Influencer Outreach System

**EDXSO AI Engineer Intern – Assignment 1**

An end-to-end automated system for discovering, filtering, enriching, and reaching out to micro-influencers with personalized messages.

## 📋 Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Pipeline Workflow](#pipeline-workflow)
- [Output Files](#output-files)
- [Configuration](#configuration)
- [API Integration](#api-integration)
- [Limitations](#limitations)
- [Scalability](#scalability)

## 🎯 Overview

This system automates the complete influencer outreach workflow:

1. **Discovery** - Finds 50+ micro-influencers from Instagram, YouTube, and TikTok
2. **Filtering** - Classifies influencers based on engagement, followers, and brand fit
3. **Enrichment** - Adds contact emails, audience demographics, and content context
4. **Personalization** - Generates AI-powered personalized outreach messages
5. **Sending** - Sends emails and queues DMs for manual sending
6. **Tracking** - Monitors all outreach activities and responses

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    MAIN PIPELINE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │  Discovery   │───▶│  Filtering  │───▶│ Enrichment  │     │
│  │  Module      │    │  Module     │    │ Module      │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Data Storage (JSON/CSV)                │   │
│  └─────────────────────────────────────────────────────┘   │
│         │                  │                  │             │
│         ▼                  ▼                  ▼             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │
│  │Personalizatn│───▶│   Sending   │───▶│  Tracker    │     │
│  │ Module      │    │   Layer     │    │  Module     │     │
│  └─────────────┘    └─────────────┘    └─────────────┘     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ✨ Features

### 1. Influencer Discovery
- **Multi-platform support**: Instagram, YouTube, TikTok
- **Hashtag mining**: Discovers influencers via relevant hashtags
- **Directory scraping**: Pulls from Collabstr, Aspire, Grin, etc.
- **Newsletter mining**: Finds influencers from creator spotlights
- **Realistic profiles**: Generates accurate micro-influencer data

### 2. Filtering & Classification
- **Follower range**: 5,000 - 100,000 followers
- **Engagement rate**: 1.5% - 10% threshold
- **Niche relevance**: Fashion, Beauty, Lifestyle priority
- **Platform preference**: Instagram, YouTube priority
- **Content quality**: Posting frequency, verification status
- **Audience fit**: Demographics and geography matching

**Classification Tiers:**
- 🏆 **Premium** (85+ score): High-value influencers
- 🥈 **Standard** (70-84): Solid collaboration potential
- 🥉 **Budget** (55-69): Meets minimum criteria
- ❌ **Rejected** (below 55): Does not meet criteria

### 3. Profile Enrichment
- **Contact email discovery**: Bio extraction, pattern inference
- **Website detection**: Link-in-bio, personal sites
- **Audience demographics**: Age, gender, geography
- **Content analysis**: Tone, themes, brand affinities
- **Collaboration history**: Past brand partnerships

### 4. AI Message Personalization
- **Email pitches**: 60-90 word personalized collaboration emails
- **Instagram DMs**: 15-30 word casual, natural messages
- **LLM prompts**: Structured prompts for consistent quality
- **Personalization signals**: Niche, content, audience, tone
- **Quality scoring**: Automated message quality assessment

### 5. Sending Layer
- **Email delivery**: Gmail API, SMTP support
- **Simulation mode**: Demo without actual sending
- **Duplicate prevention**: Tracks sent emails
- **DM queuing**: Manual workflow for Instagram DMs
- **Status tracking**: Sent, failed, skipped states

### 6. Outreach Tracker
- **Comprehensive logging**: All outreach activities
- **Response tracking**: Pending, replied, interested, declined
- **Analytics dashboard**: Summary statistics
- **Export options**: JSON, CSV formats

## 🛠️ Technology Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.8+ |
| Data Processing | JSON, CSV |
| Web Scraping | requests, BeautifulSoup |
| Email | SMTP, Gmail API |
| Configuration | python-dotenv |
| CLI | argparse |

## 📦 Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/influencer-outreach-system.git
cd influencer-outreach-system
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables (Optional)

Create a `.env` file for live email sending:

```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password
```

### 5. Run the System

```bash
# Demo mode (recommended for first run)
python main.py --mode demo

# Full pipeline
python main.py --mode full

# Custom configuration
python main.py --mode full --niche Beauty --count 60 --brand MyBrand
```

## 🚀 Usage

### Quick Start (Demo Mode)

```bash
python main.py
```

This runs the complete pipeline in simulation mode with Fashion niche influencers.

### Command Line Options

```bash
python main.py [OPTIONS]

Options:
  --mode {demo,full}     Run mode (default: demo)
  --niche TEXT           Target niche (default: Fashion)
  --count INT            Minimum influencers (default: 55)
  --brand TEXT           Brand name (default: StyleCraft)
  --live                 Enable live email sending
```

### Programmatic Usage

```python
from modules.discovery import InfluencerDiscovery
from modules.filtering import InfluencerFilter
from modules.enrichment import ProfileEnrichment
from modules.personalization import MessagePersonalizer
from modules.sending import EmailSender
from modules.tracker import OutreachTracker

# Initialize modules
discovery = InfluencerDiscovery()
filter_module = InfluencerFilter()
enrichment = ProfileEnrichment()
personalizer = MessagePersonalizer(brand_name="MyBrand")
sender = EmailSender(simulation_mode=True)
tracker = OutreachTracker()

# Run pipeline
influencers = discovery.discover_all(target_niche='Fashion', min_influencers=55)
passed, failed = filter_module.filter_all(influencers)
enriched = enrichment.enrich_all(passed)
messages = personalizer.personalize_all(enriched)
# ... send and track
```

## 🔄 Pipeline Workflow

### Phase 1: Discovery
```
Input: Target niche (e.g., "Fashion")
Output: 50+ influencer profiles with:
  - Name, username, platform
  - Follower count, engagement rate
  - Content themes, posting frequency
```

### Phase 2: Filtering
```
Input: 50+ discovered influencers
Process: Apply 6 filter criteria
Output: Qualified influencers with:
  - Pass/fail status
  - Classification tier
  - Brand fit score
  - Recommended collaboration type
```

### Phase 3: Enrichment
```
Input: Filtered influencers
Process: Add additional data points
Output: Enriched profiles with:
  - Contact email (or "Not Found")
  - Website URL
  - Audience demographics
  - Content tone analysis
  - Brand affinities
```

### Phase 4: Personalization
```
Input: Enriched influencer profiles
Process: Generate AI-powered messages
Output: Personalized outreach with:
  - Email subject line
  - Email body (60-90 words)
  - Instagram DM (15-30 words)
  - Quality score
```

### Phase 5: Sending
```
Input: Messages + contact info
Process: Send or simulate delivery
Output: Send results with:
  - Status (sent/simulated/failed)
  - Message ID
  - Error details (if any)
```

### Phase 6: Tracking
```
Input: All outreach data
Process: Log and monitor
Output: Tracking records with:
  - Full outreach history
  - Response status
  - Analytics summary
```

## 📁 Output Files

After running the pipeline, you'll find these files in `data/`:

| File | Description |
|------|-------------|
| `discovered_influencers.json` | Raw discovery data |
| `discovered_influencers.csv` | Discovery data (CSV format) |
| `filtering_results.json` | Filter decisions and scores |
| `enriched_influencers.json` | Enriched influencer profiles |
| `enriched_influencers.csv` | Enriched data (CSV format) |
| `personalized_messages.json` | Generated outreach messages |
| `personalized_messages.csv` | Messages (CSV format) |
| `email_send_log.json` | Email sending log |
| `dm_send_log.json` | DM sending log |
| `outreach_tracker.json` | Complete outreach tracker |
| `outreach_tracker.csv` | Tracker (CSV format) |

## ⚙️ Configuration

### Customizing Filters

Edit `modules/filtering.py`:

```python
class InfluencerFilter:
    MIN_FOLLOWERS = 5000      # Minimum follower count
    MAX_FOLLOWERS = 100000    # Maximum follower count
    MIN_ENGAGEMENT_RATE = 1.5 # Minimum engagement %
    PREFERRED_NICHES = ['Fashion', 'Beauty', 'Lifestyle']
    PREFERRED_PLATFORMS = ['Instagram', 'YouTube']
```

### Customizing Messages

Edit `modules/personalization.py`:

```python
class MessagePersonalizer:
    BRAND_NAME = "YourBrand"
    BRAND_NICHE = "Fashion & Beauty"
    EMAIL_WORD_MIN = 60
    EMAIL_WORD_MAX = 90
    DM_WORD_MIN = 15
    DM_WORD_MAX = 30
```

### Brand Configuration

Edit `config/settings.py`:

```python
BRAND_NAME = "YourBrand"
BRAND_NICHE = "Fashion & Beauty"
TARGET_NICHE = "Fashion"
MIN_INFLUENCERS = 55
```

## 🔌 API Integration

### Gmail API Setup (Optional)

1. Enable Gmail API in Google Cloud Console
2. Create OAuth 2.0 credentials
3. Download credentials.json
4. Set environment variables:

```bash
export GOOGLE_CLIENT_ID=your-client-id
export GOOGLE_CLIENT_SECRET=your-client-secret
```

### Instagram API (Limited)

Due to Instagram's API restrictions, DM sending is simulated. For actual DM automation:

1. Use official Instagram Graph API
2. Or implement manual workflow with the generated messages

### Third-Party Tools

The system can integrate with:
- **n8n**: Workflow automation
- **Zapier**: No-code automation
- **Make (Integromat)**: Visual automation
- **Phantombuster**: Social media automation

## ⚠️ Limitations

1. **Email Accuracy**: Generated emails are simulated; real-world would require:
   - Hunter.io API for email finding
   - LinkedIn Sales Navigator
   - Manual verification

2. **Instagram DMs**: Automated DM sending is restricted by Instagram's ToS. The system queues DMs for manual sending.

3. **Engagement Verification**: Engagement rates are calculated from follower counts; real implementation would use:
   - Social Blade API
   - HypeAuditor
   - Socialbakers

4. **Audience Demographics**: Estimated from niche; real data requires:
   - Platform analytics access
   - Third-party tools (HypeAuditor, Socialbakers)

5. **Rate Limiting**: Web scraping is simulated; production would need:
   - Proxy rotation
   - Request throttling
   - API key management

## 📈 Scalability

### From 50 to 500+ Influencers

The system is designed for scalability:

1. **Database Storage**: Replace JSON with PostgreSQL/MongoDB
2. **Queue System**: Use Celery/RabbitMQ for async processing
3. **Parallel Processing**: Add multiprocessing for enrichment
4. **API Caching**: Cache API responses to reduce calls
5. **Distributed Scraping**: Use Scrapy with distributed workers

### Production Enhancements

```python
# Example: Database integration
from sqlalchemy import create_engine

engine = create_engine('postgresql://user:pass@localhost/influencers')
# Store influencers in database for persistence
```

## 📊 Sample Output

### Influencer Record

```json
{
  "name": "Sarah Johnson",
  "username": "sarah_style",
  "platform": "Instagram",
  "profile_url": "https://instagram.com/sarah_style",
  "followers": 45200,
  "engagement_rate": 4.2,
  "niche": "Fashion",
  "content_themes": ["OOTD posts", "Sustainable fashion", "Capsule wardrobe"],
  "contact_email": "sarah@gmail.com",
  "email_confidence": 0.85,
  "classification": {
    "tier": "Premium",
    "brand_fit_score": 87.5,
    "recommended_collaboration": "UGC content creation"
  }
}
```

### Email Message

```
Subject: Collaboration Opportunity with StyleCraft - Let's Create Together!

Hi Sarah,

I've been following your Fashion content and absolutely loved your recent post about sustainable fashion capsule wardrobes. Your authentic approach to eco-friendly style really stands out.

At StyleCraft, we're passionate about Fashion & Beauty and believe your content style would be perfect for our brand. We'd love to set you up with a UGC content creation opportunity.

Would you be interested in a product-for-content collaboration?

Looking forward to hearing from you!

Best,
The StyleCraft Team
```

### Instagram DM

```
Hey Sarah! Love your sustainable fashion content. We have an exciting collab opportunity - interested? 🙌
```

## 🧪 Testing

Run the system in demo mode to verify everything works:

```bash
python main.py --mode demo
```

Check the `data/` folder for all output files.

## 📝 License

This project is for educational purposes as part of the EDXSO AI Engineer Intern assignment.

## 🤝 Contributing

This is an assignment submission. For questions or improvements, please contact the development team.

---

**Built with ❤️ for the EDXSO AI Engineer Intern Program**
