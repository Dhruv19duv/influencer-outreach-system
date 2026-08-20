"""
Configuration Settings for Influencer Outreach System
Customize these settings to match your brand and requirements.
"""

# Brand Configuration
BRAND_NAME = "StyleCraft"
BRAND_NICHE = "Fashion & Beauty"
BRAND_DESCRIPTION = "A modern fashion and beauty brand focused on sustainable, affordable style."

# Discovery Configuration
TARGET_NICHE = "Fashion"  # Primary niche to target
MIN_INFLUENCERS = 55  # Minimum influencers to discover
PLATFORMS = ["Instagram", "YouTube", "TikTok"]  # Platforms to search

# Micro-influencer Definition
MIN_FOLLOWERS = 5000
MAX_FOLLOWERS = 100000
MIN_ENGAGEMENT_RATE = 1.5  # Percentage
MAX_ENGAGEMENT_RATE = 10.0  # Percentage

# Filtering Configuration
PREFERRED_NICHES = ["Fashion", "Beauty", "Lifestyle"]
PREFERRED_PLATFORMS = ["Instagram", "YouTube"]
PREFERRED_REGIONS = [
    "United States", "United Kingdom", "Canada",
    "Australia", "Europe", "North America"
]

# Content Themes by Niche
CONTENT_THEMES = {
    "Fashion": [
        "OOTD posts", "Thrift hauls", "Sustainable fashion",
        "Streetwear", "Capsule wardrobe", "Seasonal trends",
        "Accessory styling", "Budget fashion", "Designer dupes",
        "Vintage finds"
    ],
    "Beauty": [
        "Skincare routines", "Makeup tutorials", "Product reviews",
        "Hair care", "Clean beauty", "Anti-aging",
        "K-beauty", "Drugstore finds", "Luxury beauty",
        "Nail art"
    ]
}

# Message Personalization
EMAIL_WORD_MIN = 60
EMAIL_WORD_MAX = 90
DM_WORD_MIN = 15
DM_WORD_MAX = 30

# Collaboration Types
COLLABORATION_TYPES = [
    "Sponsorship",
    "Affiliate campaign",
    "UGC content creation",
    "Brand ambassador program",
    "Paid product placement",
    "Barter collaboration"
]

# Sending Configuration
SIMULATION_MODE = True  # Set to False to actually send emails
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = ""  # Set via environment variable
SMTP_PASS = ""  # Set via environment variable

# Output Configuration
OUTPUT_DIR = "data"
SAVE_JSON = True
SAVE_CSV = True

# Rate Limiting
REQUEST_DELAY = 0.1  # Seconds between API requests
BATCH_SIZE = 10  # Process in batches

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "data/pipeline.log"
