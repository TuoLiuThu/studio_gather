import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FIRECRAWL_API_KEY = os.getenv("FIRECRAWL_API_KEY")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_SENDER = os.getenv("EMAIL_SENDER")
EMAIL_RECIPIENT = os.getenv("EMAIL_RECIPIENT")
# 建议：确保这个 KEY 是用新号申请的，不要用主号的
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") 

# === 新增：指定 Cookies 文件路径 ===
# 这里的路径指向你刚导出的新号 Cookies
YOUTUBE_COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies_burner.txt')

DATA_SOURCES = {
    # ... 保持不变 ...
    "Hardware & Semi": [
        {
            "name": "SemiAnalysis",
            "url": "https://newsletter.semianalysis.com/feed", 
            "type": "rss"
        },
        {
            "name": "Dwarkesh Podcast", 
            "channel_id": "UCXl4i9dYBrFOabk0xGmbkRA", 
            "type": "youtube"
        }
    ]
}

LOOKBACK_HOURS = 250