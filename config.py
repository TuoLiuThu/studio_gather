import os
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER", "your_email@gmail.com")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT", "recipient@example.com")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

# Data Sources
# Structure: Category -> List of Sources
# Source keys: 'name', 'url', 'type' (rss, youtube, website), 'channel_id' (for youtube)

DATA_SOURCES = {
    "Hardware & Semi": [
        {
            "name": "SemiAnalysis",
            "url": "https://newsletter.semianalysis.com/feed", # Assuming RSS feed exists at /feed
            "type": "rss"
        },
        # 这里是你新添加的 Dwarkesh Patel
        {
            "name": "Dwarkesh Podcast", 
            "channel_id": "UCXl4i9dYBrFOabk0xGmbkRA", 
            "type": "youtube"
        }
        # Add more sources here as needed
        # {
        #     "name": "NVIDIA YouTube",
        #     "channel_id": "UC...", 
        #     "type": "youtube"
        # }
    ]
}

# Configuration for Discovery
LOOKBACK_HOURS = 250



