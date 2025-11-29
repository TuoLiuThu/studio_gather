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
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY") 

# 指定 Cookies 文件路径
YOUTUBE_COOKIES_PATH = os.path.join(os.path.dirname(__file__), 'cookies_burner.txt')

DATA_SOURCES = {
    # 1. AI 深度技术与工程
    "AI Engineering & Tech": [
        {
            "name": "Latent Space",
            "url": "https://api.substack.com/feed/podcast/1075368.rss",
            "type": "rss"
        },
        {
            "name": "Oxide and Friends",
            "url": "https://feeds.transistor.fm/oxide-and-friends",
            "type": "rss"
        },
        {
            "name": "SemiAnalysis",
            "url": "https://newsletter.semianalysis.com/feed", 
            "type": "rss"
        }
    ],

    # 2. 行业新闻与硬核半导体
    "Industry & Hardware": [
        {
            "name": "The AI Daily Brief",
            "url": "https://feeds.megaphone.fm/theaibreakdown",
            "type": "rss"
        },
        {
            "name": "Fabricated Knowledge",
            "url": "https://api.substack.com/feed/podcast/399088.rss",
            "type": "rss"
        }
    ],

    # 3. 商业、创投与历史 (VC & Business)
    "VC & Business Strategy": [
        {
            "name": "Acquired",
            "url": "https://feeds.transistor.fm/acquired",
            "type": "rss"
        },
        {
            "name": "Dwarkesh Podcast",
            "url": "https://www.dwarkesh.com/feed",
            "type": "rss"
        },
        # 使用 Apple ID 动态解析，防止源地址变动
        {
            "name": "No Priors",
            "apple_id": "1668002688", 
            "type": "apple_podcast"
        }
    ],

    # 4. 中文优质创投 (Chinese Tech & VC)
    "Chinese Tech Insights": [
        {
            "name": "OnBoard!",
            "apple_id": "1613083252",
            "type": "apple_podcast"
        },
        {
            "name": "乱翻书",
            "apple_id": "1591595410",
            "type": "apple_podcast"
        },
        {
            "name": "42章经",
            "apple_id": "1700299886",
            "type": "apple_podcast"
        }
    ]
}

LOOKBACK_HOURS = 200  # 建议改为 24 或 48 小时，250 小时会导致每次抓取量过大

